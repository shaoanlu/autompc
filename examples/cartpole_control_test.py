import time
from pdb import set_trace
import sys, os, io
sys.path.append(os.getcwd() + "/..")

import numpy as np
import autompc as ampc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import argparse
import pickle
from joblib import Memory
import torch

from scipy.integrate import solve_ivp

memory = Memory("cache")

cartpole = ampc.System(["theta", "omega", "x", "dx"], ["u"])

def cartpole_dynamics(y, u, g = 9.8, m_c = 1, m_p = 1, L = 1, b = 1.0):
    """
    Parameters
    ----------
        y : states
        u : control

    Returns
    -------
        A list describing the dynamics of the cart cart pole
    """
    theta, omega, x, dx = y
    return np.array([omega,
            1.0/(L*(m_c+m_p+m_p*np.sin(theta)**2))*(-u*np.cos(theta) 
                - m_p*L*omega**2*np.cos(theta)*np.sin(theta)
                - (m_c+m_p+m_p)*g*np.sin(theta)
                - b*omega),
            dx,
            1.0/(m_c + m_p*np.sin(theta)**2)*(u + m_p*np.sin(theta)*
                (L*omega**2 + g*np.cos(theta)))])

def cartpole_simp_dynamics(y, u, g = 9.8, m = 1, L = 1, b = 0.1):
    """
    Parameters
    ----------
        y : states
        u : control

    Returns
    -------
        A list describing the dynamics of the cart cart pole
    """
    theta, omega, x, dx = y
    return np.array([omega,
            g * np.sin(theta)/L - b * omega / (m*L**2) + u * np.cos(theta)/L,
            dx,
            u])

def dt_cartpole_dynamics(y,u,dt,g=9.8,m=1,L=1,b=1.0):
    y = np.copy(y)
    #y[0] += np.pi
    #sol = solve_ivp(lambda t, y: cartpole_dynamics(y, u, g, m, L, b), (0, dt), y, t_eval = [dt])
    #if not sol.success:
    #    raise Exception("Integration failed due to {}".format(sol.message))
    #y = sol.y.reshape((4,))
    y += dt * cartpole_simp_dynamics(y,u[0],g,m,L,b)
    #y[0] -= np.pi
    return y

def animate_cartpole(fig, ax, dt, traj):
    ax.grid()

    line, = ax.plot([0.0, 0.0], [0.0, -1.0], 'o-', lw=2)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    ctrl_text = ax.text(0.7, 0.95, '', transform=ax.transAxes)

    def init():
        line.set_data([0.0, 0.0], [0.0, -1.0])
        time_text.set_text('')
        return line, time_text

    def animate(i):
        #i = min(i, ts.shape[0])
        line.set_data([traj[i,"x"], traj[i,"x"]+np.sin(traj[i,"theta"]+np.pi)], 
                [0, -np.cos(traj[i,"theta"] + np.pi)])
        time_text.set_text('t={:.2f}'.format(dt*i))
        ctrl_text.set_text("u={:.2f}".format(traj[i,"u"]))
        return line, time_text

    ani = animation.FuncAnimation(fig, animate, frames=traj.size, interval=dt*1000,
            blit=False, init_func=init, repeat_delay=1000)

    return ani

dt = 0.05
cartpole.dt = dt

umin = -20.0
umax = 20.0
udmax = 0.25

# Generate trajectories for training
num_trajs = 500

@memory.cache
def gen_trajs(traj_len, num_trajs=num_trajs, dt=dt):
    rng = np.random.default_rng(49)
    trajs = []
    for _ in range(num_trajs):
        theta0 = rng.uniform(-0.002, 0.002, 1)[0]
        y = [theta0, 0.0, 0.0, 0.0]
        traj = ampc.zeros(cartpole, traj_len)
        for i in range(traj_len):
            traj[i].obs[:] = y
            #if u[0] > umax:
            #    u[0] = umax
            #if u[0] < umin:
            #    u[0] = umin
            #u += rng.uniform(-udmax, udmax, 1)
            u  = rng.uniform(umin, umax, 1)
            y = dt_cartpole_dynamics(y, u, dt)
            traj[i].ctrl[:] = u
        trajs.append(traj)
    return trajs
trajs = gen_trajs(4)
trajs2 = gen_trajs(200)

from autompc.sysid import (GaussianProcess, 
        LargeGaussianProcess, 
        ApproximateGaussianProcess)
from autompc.control import IterativeLQR

@memory.cache
def train_approx_gp_inner(num_trajs):
    cs = ApproximateGaussianProcess.get_configuration_space(cartpole)
    cfg = cs.get_default_configuration()
    model = ampc.make_model(cartpole, ApproximateGaussianProcess, cfg)
    model.train(trajs2[-num_trajs:])
    return model.get_parameters()

def train_approx_gp(num_trajs):
    cs = ApproximateGaussianProcess.get_configuration_space(cartpole)
    cfg = cs.get_default_configuration()
    model = ampc.make_model(cartpole, ApproximateGaussianProcess, cfg)
    params = train_approx_gp_inner(num_trajs)
    model.set_parameters(params)
    return model

def init_ilqr(model, task):
    hori = 21  # hori means integer horizon... how many steps...
    ubound = np.array([[-15], [15]])
    mode = 'auglag'
    ilqr = IterativeLQR(cartpole, task, model, hori, reuse_feedback=20, 
            verbose=True)
    return ilqr

@memory.cache
def run_experiment(model_name, controller_name, init_state):
    if model_name == "approx_gp":
        model = train_approx_gp(25)


    # Now it's time to apply the controller
    task1 = ampc.Task(cartpole)
    Q = np.diag([1.0, 1.0, 1.0, 1.0])
    R = np.diag([1.0]) * 0.01
    F = np.diag([10., 10., 10., 10.])*10.0
    task1.set_quad_cost(Q, R, F)

    if controller_name == "ilqr":
        con = init_ilqr(model, task1)

    # just give a random initial state
    sim_traj = ampc.zeros(cartpole, 1)
    x = np.array([0.01, 0, 0, 0])
    sim_traj[0].obs[:] = x
    us = []


    constate = con.traj_to_state(sim_traj[:1])
    for step in range(200):
        u, constate = con.run(constate, sim_traj[-1].obs)
        print('u = ', u, 'state = ', sim_traj[-1].obs)
        x = dt_cartpole_dynamics(sim_traj[-1].obs, u, dt)
        # x = model.pred(sim_traj[-1].obs, u)
        sim_traj[-1, "u"] = u
        sim_traj = ampc.extend(sim_traj, [x], [[0.0]])
        us.append(u)
    return sim_traj

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, choices=["approx_gp"], 
            default = "approx_gp", help="Specify which system id model to use")
    parser.add_argument("--controller", type=str, choices=["ilqr"], 
            default = "ilqr", help="Specify which nonlinear controller to use")
    parser.add_argument("--init_angle", type=float, default=0.1,
            help="Specify the initial angle for the simulation.")
    args = parser.parse_args()

    dt = 0.05
    cartpole.dt = dt

    init_state = np.array([args.init_angle, 0.0, 0.0, 0.0])
    sim_traj = run_experiment(args.model, args.controller, init_state)
    set_trace()

    print(sim_traj.obs)
    fig = plt.figure()
    ax = fig.gca()
    ax.set_aspect("equal")
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ani = animate_cartpole(fig, ax, dt, sim_traj)
    #ani.save("out/cartpole_test/aug31_02.mp4")
    plt.show()

if __name__ == "__main__":
    main()