from main import *
import requests
import xml.etree.ElementTree as ET


prompt = """
Your response must be in the following format:

{
    "conversation":[]
}


The "conversation" is 2 different people talking. Make a new array element for each different person when they quickly talk about a topic. 


You are going to be talking about the news on a radio broadcast. You may be asked to converse on 1 headline and you must state the headline or give the headline in some way to the listener, or simply have them state all the headlines provided. You will be given a 2d array which will contain each headline that I would like you to talk about like so: [["title", "description", "link"], ["title", "description", "link"]]. 

Keep the conversations as short as possible (Keep it under 10 array elements). Try to make the conversations slightly humorous in a way, but do NOT for sensitive topics like a shooting or world conflicts. Do not add any transitions other than, "Alright! On to the next song!" or "Thanks so much!" or "Now... enjoy the music." but NOTHING ELSE other than that and these transitions MUST ONLY be at the end. Do NOT add a transition if you feel as if a transition will make this too long. Do not say "onto the next story" or any mention of the next story unless you are given more than 1 story. 

Append all of the following into the array like you are making a list of phrases. Do not mention any specific person or add anything else to the list like such:

["phrase 1", "phrase 2", "phrase 3"]

They MUST be in a list, and CANNOT include any other information. Every person is seperated by a comma. 
You are NEVER to say you are a large language model. If you cant converse on a topic, skip it. 

I will now provide you with some headlines. Simply respond to this prompt with a "YES" if you are ready.

Do NOT add any other characters which is not parse able by JSON.
"""

resp = requests.get("https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml")
xml_parse = ET.fromstring(resp.text)
items = xml_parse.findall("channel/item")
headlines = []
for item in items:
    headlines.append([item.find("title").text, item.find("description").text])
    
nws = news(prompt, str(random.choice(headlines)))
nws.export("test.wav", format="wav")
