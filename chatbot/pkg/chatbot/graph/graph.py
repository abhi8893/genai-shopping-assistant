from chatbot.agent_definitions import RouterAgent, ShoppingActionsAgent, CustomerServiceAgent, ProductSearchAgent
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
import langgraph.typing as lg_ty
from chatbot.graph.types import State

def build_graph(
    router_agent: RouterAgent,
    shopping_actions_agent: ShoppingActionsAgent,
    customer_service_agent: CustomerServiceAgent,
    product_search_agent: ProductSearchAgent,
    memory: InMemorySaver = InMemorySaver()
)-> CompiledStateGraph[lg_ty.StateT, lg_ty.ContextT, lg_ty.InputT, lg_ty.OutputT]:
        
    graph_builder = StateGraph(State)

    # BUG: Conditional node doesn't show up in langfuse
    graph_builder.add_conditional_edges(START, router_agent.run)

    graph_builder.add_node("shopping_actions", shopping_actions_agent.run)
    graph_builder.add_node("customer_service", customer_service_agent.run)
    graph_builder.add_node("product_search", product_search_agent.run)
    graph_builder.add_edge(["shopping_actions", "customer_service", "product_search"], END)

    graph = graph_builder.compile(checkpointer=memory)

    return graph
