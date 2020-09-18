# Created by William Edwards (wre2@illinois.edu)

from pdb import set_trace
import ConfigSpace as CS
import ConfigSpace.hyperparameters as CSH
import ConfigSpace.conditions as CSC

from ..cs_utils import *
from ..utils import *

class FixedControlPipeline:
    def __init__(self, system, task, Model, Controller, task_transformers):
        self.system = system
        self.task = task
        self.Model = Model
        self.Controller = Controller
        self.task_transformers = task_transformers[:]


    def get_configuration_space(self):
        cs = CS.ConfigurationSpace()
        model_cs = self.Model.get_configuration_space(self.system)
        add_configuration_space(cs, "_model", model_cs)
        contr_cs = self.Controller.get_configuration_space(self.system, self.task,
                self.Model)
        add_configuration_space(cs, "_controller", contr_cs)
        for i, trans in enumerate(self.task_transformers):
            trans_cs = trans.get_configuration_space(self.system)
            add_configuration_space(cs, "_task_transformer_{}".format(i), trans_cs)
        return cs

    def __call__(self, cfg, trajs):
        # First instantiate and train the model
        model_cs = self.Model.get_configuration_space(self.system)
        model_cfg = model_cs.get_default_configuration()
        set_subspace_configuration(cfg, "_model", model_cfg)
        model = make_model(self.system, self.Model, model_cfg)
        model.train(trajs)

        # Next set up task
        task = self.task
        for i, Trans in enumerate(self.task_transformers):
            trans_cs = Trans.get_configuration_space(self.system)
            trans_cfg = trans_cs.get_default_configuration()
            set_subspace_configuration(cfg, "_task_transformer_{}".format(i), trans_cfg)
            trans = make_transformer(self.system, Trans, trans_cfg)
            task = trans(task)

        # Finally create the controller
        contr_cs = self.Controller.get_configuration_space(self.system, self.task,
                model)
        contr_cfg = contr_cs.get_default_configuration()
        set_subspace_configuration(cfg, "_controller", contr_cfg)
        controller = make_controller(self.system, task, model, self.Controller, contr_cfg)

        return controller, model

        
