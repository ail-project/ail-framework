#!/usr/bin/env python3
# -*-coding:UTF-8 -*

"""
The LLM-Extractor Module
================================

This module extracts geolocation information from an unstructured text

"""

##################################
# Import External packages
##################################
from modules.abstract_module import AbstractModule
import os
import sys
from openai import Client
from itertools import chain
from pprint import pprint
from typing import List, Dict
from lib.ConfigLoader import ConfigLoader


sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
# from lib.ConfigLoader import ConfigLoader
# from lib import Statistics


class LLMExtractor(AbstractModule):

    def __init__(self, queue=True):
        super(LLMExtractor, self).__init__(queue=queue)

        config_loader = ConfigLoader()

        # Waiting time in seconds between to message processed
        self.pending_seconds = 0

        # Send module state to logs
        self.logger.info(f'Module {self.module_name} initialized')
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            assert False, "API key not found. Please set the OPENAI_API_KEY environment variable."

        #   or take it from the config file:    api_key=config_loader.get_config_str("OpenAI", "OPENAI_API_KEY"))
        self.openai_client = Client(api_key=self.api_key)
        self.model = 'o3-mini'

    def find_geolocation(self, text: str) -> List[Dict]:
        """find all occurences of geolocation information in the given text
        Returns:
            List[Dict]: list of geolocation information
        Example:
            [
                {"location": "San Francisco", "type": "city", "latitude": 37.8176155, "longitude": -122.4783123},
                {"location": "Terrace Avenue, Fresno County, California", "type": "full_address", "latitude": 36.7783, "longitude": -119.4179},
                {"location": "USA", "type": "country", "latitude": 37.0902, "longitude": -95.7129},
            ]
        """

        prompt = """
You are a highly skilled geospatial intelligence analyst, adept at extracting precise geolocation information from unstructured text. Please analyze the following text and identify all references to locations. Then, return only a JSON array of objects in the format:

[
{
"location": "<location string>",
"type": "<most specific type from: full_address, city, country, region, continent, ocean, sea, river, mountain, lake>",
"latitude": "<decimal degrees>",
"longitude": "<decimal degrees>"
}
]

Instructions:

For each mention of a place, use the most specific location type that applies (e.g., if it’s an address, use “full_address”; if it’s a city, use “city”; etc.).
Your “location” field should exactly match the text’s most specific place name or address.
“latitude” and “longitude” must be as accurate as possible for the identified location.
Do not add extra fields or information beyond the specified JSON structure.
Return only the JSON array, with no additional explanation or text.
Example:
[
{
"location": "San Francisco",
"type": "city",
"latitude": 37.7749,
"longitude": -122.4194
},
{
"location": "Terrace Avenue, Fresno County, California",
"type": "full_address",
"latitude": 36.7783,
"longitude": -119.4179
},
{
"location": "USA",
"type": "country",
"latitude": 37.0902,
"longitude": -95.7129
}
]

Now, process the text below and return the resulting JSON. Do not include any additional commentary.

Text to analyze:
{{text}}
        """

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            response_format={
                "type": "json_object",
            },
            reasoning_effort="medium",
            # temperature=0,    # for other models
            store=False
        )
        # pprint(response, indent=4)

        # Extract the geolocation information from the response
        geolocation_info = [
            answer.message.content for answer in response.choices]
        return geolocation_info

    def compute(self, message):
        obj = self.get_obj()
        obj_id = obj.get_id()

        geolocations = self.find_geolocation(obj.get_content())

        print(f'Geolocation found: {geolocations}')
        if geolocations:
            # Tags
            tag = 'infoleak:automatic-detection="geolocation"'
            self.add_message_to_queue(message=tag, queue='Tags')


if __name__ == '__main__':

    module = LLMExtractor()
    module.run()
