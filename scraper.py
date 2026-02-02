import requests
from bs4 import BeautifulSoup


def get_israeli_swimmers():
    url = "https://en.wikipedia.org/wiki/Category:Olympic_swimmers_for_Israel"

    # --- ADD A USER-AGENT ---
    # This tells Wikipedia: "I am a browser, not a bot."
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Connecting to {url}...")

    # Pass the headers here
    response = requests.get(url, headers=headers)

    # Check if it worked (200 means OK)
    if response.status_code != 200:
        print(f"Error: Status Code {response.status_code}. Wikipedia blocked us.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    names = []
    category_div = soup.find("div", {"id": "mw-pages"})

    if category_div:
        links = category_div.find_all("a")
        for link in links:
            name = link.text
            # Basic cleanup
            if "Category:" not in name and "Template:" not in name:
                names.append(name)

    return names


if __name__ == "__main__":
    swimmers = get_israeli_swimmers()

    print(f"Found {len(swimmers)} swimmers!")

    with open("swimmers_list.txt", "w", encoding="utf-8") as f:
        for name in swimmers:
            f.write(name + "\n")

    print("✅ Successfully saved names to 'swimmers_list.txt'")
