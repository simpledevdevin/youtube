from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class HotTake():
    """HotTake crew"""

    # agents: list[BaseAgent]
    # tasks: list[Task]

    # technically this is not needed because of the @CrewBase decorator
    # but is nice to explicitly spell out
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def moderator(self) -> Agent:
        return Agent(
            config=self.agents_config['moderator'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def junior_debator(self) -> Agent:
        return Agent(
            config=self.agents_config['junior_debator'], 
            verbose=True
        )

    @agent
    def senior_debator(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_debator'], 
            verbose=True
        )

    @agent
    def counter_debator(self) -> Agent:
        return Agent(
            config=self.agents_config['counter_debator'], 
            verbose=True
        )

    @task
    def generate_topic_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_topic_task'],
            output_file='outputs/topic.md'
        )

    @task
    def generate_hot_take_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_hot_take_task'], 
            output_file='outputs/hot_take.md'
        )

    @task
    def improve_hot_take_task(self) -> Task:
        return Task(
            config=self.tasks_config['improve_hot_take_task'], 
            output_file='outputs/improved_hot_take.md'
        )
    
    @task
    def counter_hot_take_task(self) -> Task:
        return Task(
            config=self.tasks_config['counter_hot_take_task'], 
            output_file='outputs/counter_hot_take.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the HotTake crew"""


        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential, # Process is the order in which the agents and tasks are executed
            verbose=True, # Whether to print the logs
        )
