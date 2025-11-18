import uuid
import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart
)

PUBLIC_AGENT_CARD_PATH = "./agent_card.json"
BASE_URL = "http://localhost:9999"

async def main()->None:
    async with httpx.AsyncClient() as http_client:
        resolver = A2ACardResolver(
            httpx_client=http_client,
            base_url=BASE_URL
        )

        final_agent_card_to_use = AgentCard | None = None

        try:
            print(f"Fetching public agent card from {BASE_URL}{PUBLIC_AGENT_CARD_PATH}")
            _public_agent_card = await resolver.get_agent_card()
            print(f"Public agent card fetched")
            print(_public_agent_card.model_dump_json(indent=2))

            final_agent_card_to_use = _public_agent_card

        except Exception as e:
            print(f"Failed to fetch public agent card: {e}")
            raise RuntimeError(f"Failed to fetch public agent card")
        
        client = A2AClient(httpx_client=http_client, agent_card=final_agent_card_to_use)

        print("A2A Client initialized")

        message_payload = Message(
            role=Role.user,
            message_id=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text="Hello, how are you?"))],
        )

        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=message_payload),
        )

        print("Sending message...")

        response = await client.send_message(request=request)

        print("Response received:")
        print(response.model_dump_json(indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())