from steam.steam_parser import SteamParser
import asyncio
import  logging
def main():

    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger().setLevel(logging.INFO)
    logging.info("Starting the parser...")

    parser = SteamParser()
    # Start the parsing process
    asyncio.run(parser.parse())

if __name__ == "__main__":
    main()