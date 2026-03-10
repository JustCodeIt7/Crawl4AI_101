import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent, Browser, ChatGoogle, ChatGroq, ChatOllama

# Connect to your existing Chrome browser
browser = Browser(
    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    user_data_dir="~/Library/Application Support/Google/Chrome",
    profile_directory="Default",
)


# NOTE: You have to close all Chrome browsers before running this example so that we can launch chrome in debug mode.
async def main():
    llm = ChatGroq(model="",api_key=os.getenv("GROQ_API_KEY"))
    # save storage state
    agent = Agent(
        llm=llm,
        # Google blocks this approach, so we use a different search engine
        task="go to amazon.com and search for pens to draw on whiteboards",
        browser=browser,
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
