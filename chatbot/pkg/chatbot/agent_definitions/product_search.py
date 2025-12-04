
from weaviate import WeaviateClient
from chatbot.graph.types import State
from chatbot.product_retrieval import retrieve_products
from chatbot.types import ProductVectorDBRecord
from pydantic import BaseModel, Field
import openai


def get_product_list_prompt_str(products: list[ProductVectorDBRecord]) -> str:
    prod_desc_lst = []
    for idx, prod in enumerate(products):
        prod_desc = f"{idx + 1}. {prod.slug} (${prod.price})"
        prod_desc_lst.append(prod_desc)

    return '\n'.join(prod_desc_lst)

class ProductParsedDetails(BaseModel):
    category: str = Field(description="The category of the product")
    subcategory: str = Field(description="The subcategory of the product")
    min_price: float = Field(description="The minimum price of the product")
    max_price: float = Field(description="The maximum price of the product")

class ProductRetrievalAgentResponse(BaseModel):
    product_details: ProductParsedDetails | None = Field(description="The parsed details of the product. Populate ONLY if no clarification response is needed.")
    product_retrieval_query: str | None = Field(description="User query rephrased as a specific retrieval query for the product. Populate ONLY if no clarification response is needed.")
    product_clarification_response: str | None = Field(description="The clarification response for the user's query when no product details were parsed.")


class ProductSearchAgent:

    name: str = 'product_search'
    alias: str = 'Product Search'


    def __init__(self, config, openai_client: openai.OpenAI = None,  weaviate_client: WeaviateClient = None):
        self.config = config
        self.weaviate_client = weaviate_client
        self.openai_client = openai.OpenAI() if openai_client is None else openai_client


    def run(self, state: State) -> State:

        if state.prev_recommended_products is not None:
            prev_recommended_products_prompt_str = get_product_list_prompt_str(state.prev_recommended_products)
        else:
            prev_recommended_products_prompt_str = "No products have been recommended to the user so far."

        system_prompt = self.config['prompts']['system_prompt'].format(
            catalog_hierarchy_tree=self.config['catalog_hierarchy_tree'],
            prev_recommended_products=prev_recommended_products_prompt_str
        )


        input_messages = [
            {'role': 'system', 'content': system_prompt},
            *state.messages,
            {'role': 'user', 'content': state.messages[-1]['content']}
        ]
        
        response = self.openai_client.responses.parse(
            model=self.config['llm'],
            input=input_messages,
            text_format=ProductRetrievalAgentResponse
        )

        prod_retrieval_agent_response = response.output_parsed



        if prod_retrieval_agent_response.product_clarification_response:
            new_state = State(
                messages=[{'role': 'assistant', 'content': prod_retrieval_agent_response.product_clarification_response}],
                prev_recommended_products=state.prev_recommended_products
            )

            return new_state
            
        product_retrieval_response = retrieve_products(
            query=prod_retrieval_agent_response.product_retrieval_query,
            categories=[prod_retrieval_agent_response.product_details.category] if prod_retrieval_agent_response.product_details.category else None,
            subcategories=[prod_retrieval_agent_response.product_details.subcategory] if prod_retrieval_agent_response.product_details.subcategory else None,
            min_price=prod_retrieval_agent_response.product_details.min_price,
            max_price=prod_retrieval_agent_response.product_details.max_price,
            weaviate_client=self.weaviate_client
        )

        products_retrieved = [ProductVectorDBRecord(**p.properties) for p in product_retrieval_response.objects]

        if not product_retrieval_response.objects:
            asst_response = "I found no products based on your query. Can you please rephrase your query?"
        else:
            product_list_prompt_str = get_product_list_prompt_str(products_retrieved)
            asst_response = "I found the following products based on your query:\n\n" + product_list_prompt_str

        new_state = State(
            messages=[
                {"role": "assistant", "content": f'{self.alias} Agent: {asst_response}'}
            ],
            prev_recommended_products=products_retrieved,
            last_response_agent=self.name
        )

        return new_state
    
        