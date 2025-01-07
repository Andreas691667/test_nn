import logging
from abc import ABC, abstractmethod
from typing import Any

class MAPEK(ABC):
    """
    Abstract base class for MAPEK architecture with integrated logging.
    Defines the MAPEK loop and knowledge structure.
    This class should be extended by specific autonomic managers.
    """
    
    def __init__(self) -> None:
        super().__init__()
        
        # Configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Can be modified to output to a file
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Stages knowledge keys
        self.MONITOR_DATA_KEY = "MONITOR_DATA"
        self.ANALYSE_RESULT_KEY = "ANALYSE_RESULT"
        self.PLAN_RESULT_KEY = "PLAN_RESULT"
        
        # Return types
        self.UNRESOLVABLE = "UNRESOLVABLE"
        self.NO_FAULT = "NO_FAULT"
        
        self.__initialise_knowledge()

    def __initialise_knowledge(self):
        """
        Initializes the knowledge base by calling the subclass-specific 
        `initialise_knowledge` method and setting default None values for 
        monitor, analyse, and plan results.
        """
        self.knowledge = self.initialise_knowledge()
        self.knowledge.update({
            self.MONITOR_DATA_KEY: None, 
            self.ANALYSE_RESULT_KEY: None,
            self.PLAN_RESULT_KEY: None
        })

    def do_loop(self) -> None:
        """
        Executes the MAPEK loop: Monitor, Analyse, Plan, and Execute.
        Updates the knowledge base at each stage with new data, results, 
        and plans.
        """
        self.logger.info("Starting MAPEK loop.")
        
        # Monitor step
        monitor_data = self.monitor()
        self.knowledge.update({self.MONITOR_DATA_KEY: monitor_data})
        self.logger.debug(f"Monitor: Data collected - {monitor_data}")
        
        # Analyse step
        analyse_result = self.analyse(monitor_data)
        self.knowledge.update({self.ANALYSE_RESULT_KEY: analyse_result})
        self.logger.debug(f"Analyse - {analyse_result}")

        # Plan and Execute steps
        if analyse_result != self.NO_FAULT:
            self.logger.info(f"Fault detected - {analyse_result}")
            self.on_fault(analyse_result)
            
            # Plan
            plan_result = self.plan(analyse_result)
            self.knowledge.update({self.PLAN_RESULT_KEY: plan_result})
            self.logger.info(f"Plan: Generated plan - {plan_result}")
            
            if plan_result != self.UNRESOLVABLE:
                self.knowledge = self.update_knowledge_on_plan(plan_result)
                self.logger.debug(f"Updated knowledge")
                # Execute
                self.execute(plan_result)
                self.logger.info(f"Execute: Plan {plan_result} executed.")
            else:
                self.on_unresolvable_fault(analyse_result)
                self.logger.info("Fault was unresolvable.")

        else:
            self.logger.info("No fault detected.")
    
    def get_knowledge(self) -> dict:
        """
        Returns the current knowledge base.
        :return: dict representing current knowledge state.
        """
        return self.knowledge

    @abstractmethod
    def initialise_knowledge(self) -> dict:
        """
        Abstract method to initialise the knowledge base.
        Must be implemented by subclasses.
        :return: Initial knowledge as a dictionary.
        """
        return {}

    @abstractmethod
    def update_knowledge_on_plan(self, plan: Any) -> dict:
        """
        Updates the knowledge base after a plan is created.
        Must be implemented by subclasses.
        :param plan: The result of the plan stage.
        :return: Updated knowledge dictionary.
        """
        return self.knowledge
    
    @abstractmethod
    def on_unresolvable_fault(self, fault_type: Any) -> None:
        """
        Abstract method to handle unresolvable faults.
        Must be implemented by subclasses.
        :param fault_type: The type of fault detected during the Analyse step.
        """
        pass

    @abstractmethod
    def on_fault(self, fault_type: Any) -> None:
        """
        Abstract method to handle faults in the system.
        Must be implemented by subclasses.
        :param fault_type: The type of fault detected during the Analyse step.
        """
        pass

    @abstractmethod
    def monitor(self) -> Any:
        """
        Abstract method for the Monitor stage.
        Must be implemented by subclasses.
        :return: The monitored data.
        """
        pass

    @abstractmethod
    def analyse(self, data: Any) -> Any:
        """
        Abstract method for the Analyse stage.
        Must be implemented by subclasses.
        :param data: The data collected from the Monitor stage.
        :return: The result of the analysis.
        """
        pass

    @abstractmethod
    def plan(self, analyse_result: Any) -> Any:
        """
        Abstract method for the Plan stage.
        Must be implemented by subclasses.
        :param analyse_result: The result of the analysis.
        :return: The plan to resolve any issues found during the Analyse stage.
        """
        pass

    @abstractmethod
    def execute(self, plan_result: Any) -> None:
        """
        Abstract method for the Execute stage.
        Must be implemented by subclasses.
        :param plan_result: The plan to be executed.
        """
        pass
