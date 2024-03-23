import json
import openai
import csv

class SarifResultAnalyzer:
    """
    A class to analyze SARIF file results using OpenAI's GPT-4.
    """
    
    def __init__(self, sarif_file_path, openai_api_key):
        """
        Initializes the SarifResultAnalyzer with the path to a SARIF file and OpenAI API key.
        
        :param sarif_file_path: Path to the SARIF file.
        :param openai_api_key: OpenAI API key.
        """
        self.sarif_file_path = sarif_file_path
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
    
    import csv

    def extract_and_analyze_results(self):
        """
        Extracts code snippets from the SARIF file, analyzes each using OpenAI's GPT-4,
        and appends the snippet result to a CSV file.
        
        :return: A list of dictionaries, each containing a 'snippet' key with the code snippet as its value,
                and an 'ai_analysis' key with the analysis result.
        """
        results_list = []
        
        with open(self.sarif_file_path, 'r', encoding='utf-8-sig') as file:
            sarif_data = json.load(file)
        
        # Write the results to a CSV file, based on the the result schema
        with open('ai_analysis_results.csv', 'a', newline='') as csvfile:
            fieldnames = ['comma', 'separated', 'fieldnames', 'related', 'to', 'ai_analysis']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header only if the file is newly created
            if csvfile.tell() == 0:
                writer.writeheader()
            
            for run in sarif_data.get('runs', []):
                for result in run.get('results', []):
                    for location in result.get('locations', []):
                        snippet_text = location.get('physicalLocation', {}).get('region', {}).get('snippet', {}).get('text', '')
                        if snippet_text:
                            snippet_result = {'snippet': snippet_text}
                            self.analyze_results_using_llm(snippet_result)
                            results_list.append(snippet_result)
                            # Parse the ai_analysis JSON string into a Python dictionary
                            try:
                                analysis_dict = json.loads(snippet_result.get('ai_analysis', '{}'))
                            except json.JSONDecodeError:
                                analysis_dict = {}
                            # Write the analysis results to the CSV file
                            writer.writerow({ })# Write each row, based on the result schema
        
        return results_list


    def analyze_results_using_llm(self, result):
        """
        Analyzes a code snippet using OpenAI's GPT-4 and updates the result with the analysis.
        
        :param result: A dictionary containing a 'snippet' key with the code snippet as its value.
        """
        snippet = result['snippet']
        try:
            # Use the following line to connect to LM Studio API
            # client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            
            completion = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": 'system_prompt',
                    },
                    {
                        "role": "user",
                        "content": snippet,
                    },
                ],
            )
            result['ai_analysis'] = completion.choices[0].message.content
        except Exception as e:
            result['ai_analysis'] = f"Error analyzing snippet: {str(e)}"

def main():
    sarif_file_path = '<path_to_SARIF_file>.sarif'
    openai_api_key = 'OPENAI_API_KEY'
    analyzer = SarifResultAnalyzer(sarif_file_path, openai_api_key)
    analyzed_results = analyzer.extract_and_analyze_results()
    print(analyzed_results)

if __name__ == "__main__":
    main()
