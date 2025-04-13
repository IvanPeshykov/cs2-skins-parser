from steam.steam_parser import SteamParser
import asyncio

def main():
    parser = SteamParser()
    # Start the parsing process
    asyncio.run(parser.start_parsing())

if __name__ == "__main__":
    main()