import json
import requests
import csv

class SarifResultAnalyzer:
    def __init__(self, sarif_file_path):
        self.sarif_file_path = sarif_file_path
    
    def extract_and_analyze_results(self):
        results_list = []
        with open(self.sarif_file_path, 'r', encoding='utf-8-sig') as file:
            sarif_data = json.load(file)

        with open('ai_analysis_results.csv', 'a', newline='') as csvfile:
            fieldnames = ['snippet', 'ai_analysis']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            
            for run in sarif_data.get('runs', []):
                for result in run.get('results', []):
                    for location in result.get('locations', []):
                        physical_location = location.get('physicalLocation', {})
                        region = physical_location.get('region', {})
                        snippet = region.get('snippet', {})
                        snippet_text = snippet.get('text', None)

                        uri = physical_location.get('artifactLocation', {}).get('uri', None)

                        if snippet_text and uri:
                            print(snippet_text)  # Debugging: print the snippet
                            snippet_result = {'snippet': snippet_text}
                            self.analyze_results_using_llm(snippet_result, snippet_text, uri)
                            results_list.append(snippet_result)
                            writer.writerow(snippet_result)
                        else:
                            print("Warning: Missing required keys in SARIF data.")
        return results_list


    def analyze_results_using_llm(self, snippet_result, snippet_text, uri):
        try:
            file_path = f"vulnerable-abc-project/{uri}"
            code_content = get_file_content(uri)

            if code_content:
                # Fetching context lines around the snippet 
                surrounding_code_context = code_content  # Replace this with actual context if needed

                prompt = f"You are an application security expert designated as senior security engineer who look upon code and identify vulnerabilities and provide fixes for those vulnerabilities. The following code snippet has been flagged as a vulnerability:\n\n{snippet_text}\n\n Conduct a thorough security review of the provided snippet by covering full code assessing it from an application security perspective based on context:\n{surrounding_code_context}\n\n Output Format should be Name the Vulnerability. Show the Vulnerable Code. Explain How it can be Exploited and Rate Your Confidence"
                
                # Example API call
                response = requests.post(
                    'http://localhost:11434/api/generate',  # Replace with your actual API endpoint
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps({'model': "llama3.1", 'prompt': prompt,"stream": False})
                )

                # Check if response is valid JSON
                try:
                    response_data = response.json()
                    snippet_result['ai_analysis'] = response_data.get('response', 'No response field in JSON')
                except json.JSONDecodeError:
                    # If JSON decoding fails, print the raw response
                    print(f"Error decoding JSON. Response content:\n{response.text}")
                    snippet_result['ai_analysis'] = "Error: Response is not valid JSON."

            else:
                snippet_result['ai_analysis'] = "Could not retrieve file content."

        except KeyError as e:
            print(f"Warning: Could not find required key in SARIF data: {e}")
            snippet_result['ai_analysis'] = "Could not analyze due to missing data in the SARIF file."

def get_file_content(uri):
    """Fetches file content based on the provided URI."""
    relative_path = uri.replace("vulnerable-abc-project/", "")
    file_path = f"vulnerable-abc-project/{relative_path}"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Warning: Could not find file at path: {file_path}")
        return None

def main():
    sarif_file_path = '/Users/myname/Desktop/ai-secure-code-review/case-study/output.sarif'
    analyzer = SarifResultAnalyzer(sarif_file_path)
    analyzed_results = analyzer.extract_and_analyze_results()
    print(analyzed_results)

if __name__ == "__main__":
    main()
