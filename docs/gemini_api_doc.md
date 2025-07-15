**Gemini API quickstart**

This quickstart shows you how to install your SDK of choice and then make your first Gemini API request.

Python JavaScript REST Go Apps Script

Install the Gemini API library
Note: We're rolling out a new set of Gemini API libraries, the Google Gen AI SDK.
Using Python 3.9+, install the google-genai package using the following pip command:

```
pip install -q -U google-genai
```

Make your first request
Get a Gemini API key in Google AI Studio

Use the generateContent method to send a request to the Gemini API.

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)
```

***Text generation***


The Gemini API can generate text output in response to various inputs, including text, images, video, and audio. This guide shows you how to generate text using text and image inputs. It also covers streaming, chat, and system instructions.

Before you begin
Before calling the Gemini API, ensure you have your SDK of choice installed, and a Gemini API key configured and ready to use.

Text input
The simplest way to generate text using the Gemini API is to provide the model with a single text-only input, as shown in this example:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["How does AI work?"]
)
print(response.text)
Image input
The Gemini API supports multimodal inputs that combine text and media files. The following example shows how to generate text from text and image input:

Python
JavaScript
Go
REST
Apps Script

from PIL import Image
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

image = Image.open("/path/to/organ.png")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[image, "Tell me about this instrument"]
)
print(response.text)
```

***Streaming output***

By default, the model returns a response after completing the entire text generation process. You can achieve faster interactions by using streaming to return instances of GenerateContentResponse as they're generated.

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")
```

***Multi-turn conversations***

The Gemini SDK lets you collect multiple rounds of questions and responses into a chat. The chat format enables users to step incrementally toward answers and to get help with multipart problems. This SDK implementation of chat provides an interface to keep track of conversation history, but behind the scenes it uses the same generateContent method to create the response.

The following code example shows a basic chat implementation:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
chat = client.chats.create(model="gemini-2.0-flash")

response = chat.send_message("I have 2 dogs in my house.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)
```

You can also use streaming with chat, as shown in the following example:

```python
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
chat = client.chats.create(model="gemini-2.0-flash")

response = chat.send_message_stream("I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")

for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)
```

***Configuration parameters***

Every prompt you send to the model includes parameters that control how the model generates responses. You can configure these parameters, or let the model use the default options.

The following example shows how to configure model parameters:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["Explain how AI works"],
    config=types.GenerateContentConfig(
        max_output_tokens=500,
        temperature=0.1
    )
)
print(response.text)
```

Here are some of the model parameters you can configure. (Naming conventions vary by programming language.)

stopSequences: Specifies the set of character sequences (up to 5) that will stop output generation. If specified, the API will stop at the first appearance of a stop_sequence. The stop sequence won't be included as part of the response.
temperature: Controls the randomness of the output. Use higher values for more creative responses, and lower values for more deterministic responses. Values can range from [0.0, 2.0].
maxOutputTokens: Sets the maximum number of tokens to include in a candidate.
topP: Changes how the model selects tokens for output. Tokens are selected from the most to least probable until the sum of their probabilities equals the topP value. The default topP value is 0.95.
topK: Changes how the model selects tokens for output. A topK of 1 means the selected token is the most probable among all the tokens in the model's vocabulary, while a topK of 3 means that the next token is selected from among the 3 most probable using the temperature. Tokens are further filtered based on topP with the final token selected using temperature sampling.

***System instructions***

System instructions let you steer the behavior of a model based on your specific use case. When you provide system instructions, you give the model additional context to help it understand the task and generate more customized responses. The model should adhere to the system instructions over the full interaction with the user, enabling you to specify product-level behavior separate from the prompts provided by end users.

You can set system instructions when you initialize your model:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a cat. Your name is Neko."),
    contents="Hello there"
)

print(response.text)
```
Then, you can send requests to the model as usual.

**Long context**

Gemini 2.0 Flash and Gemini 1.5 Flash come with a 1-million-token context window, and Gemini 1.5 Pro comes with a 2-million-token context window. Historically, large language models (LLMs) were significantly limited by the amount of text (or tokens) that could be passed to the model at one time. The Gemini 1.5 long context window, with near-perfect retrieval (>99%), unlocks many new use cases and developer paradigms.

The code you already use for cases like text generation or multimodal inputs will work out of the box with long context.

Throughout this guide, you briefly explore the basics of the context window, how developers should think about long context, various real world use cases for long context, and ways to optimize the usage of long context.

What is a context window?
The basic way you use the Gemini models is by passing information (context) to the model, which will subsequently generate a response. An analogy for the context window is short term memory. There is a limited amount of information that can be stored in someone's short term memory, and the same is true for generative models.

You can read more about how models work under the hood in our generative models guide.

Getting started with long context
Most generative models created in the last few years were only capable of processing 8,000 tokens at a time. Newer models pushed this further by accepting 32,000 tokens or 128,000 tokens. Gemini 1.5 is the first model capable of accepting 1 million tokens, and now 2 million tokens with Gemini 1.5 Pro.

In practice, 1 million tokens would look like:

50,000 lines of code (with the standard 80 characters per line)
All the text messages you have sent in the last 5 years
8 average length English novels
Transcripts of over 200 average length podcast episodes
Even though the models can take in more and more context, much of the conventional wisdom about using large language models assumes this inherent limitation on the model, which as of 2024, is no longer the case.

Some common strategies to handle the limitation of small context windows included:

Arbitrarily dropping old messages / text from the context window as new text comes in
Summarizing previous content and replacing it with the summary when the context window gets close to being full
Using RAG with semantic search to move data out of the context window and into a vector database
Using deterministic or generative filters to remove certain text / characters from prompts to save tokens
While many of these are still relevant in certain cases, the default place to start is now just putting all of the tokens into the context window. Because Gemini models were purpose-built with a long context window, they are much more capable of in-context learning. For example, with only instructional materials (a 500-page reference grammar, a dictionary, and ≈ 400 extra parallel sentences) all provided in context, Gemini 1.5 Pro and Gemini 1.5 Flash are capable of learning to translate from English to Kalamang— a Papuan language with fewer than 200 speakers and therefore almost no online presence—with quality similar to a person who learned from the same materials.

This example underscores how you can start to think about what is possible with long context and the in-context learning capabilities of Gemini models.

Long context use cases
While the standard use case for most generative models is still text input, the Gemini 1.5 model family enables a new paradigm of multimodal use cases. These models can natively understand text, video, audio, and images. They are accompanied by the Gemini API that takes in multimodal file types for convenience.

Long form text
Text has proved to be the layer of intelligence underpinning much of the momentum around LLMs. As mentioned earlier, much of the practical limitation of LLMs was because of not having a large enough context window to do certain tasks. This led to the rapid adoption of retrieval augmented generation (RAG) and other techniques which dynamically provide the model with relevant contextual information. Now, with larger and larger context windows (currently up to 2 million on Gemini 1.5 Pro), there are new techniques becoming available which unlock new use cases.

Some emerging and standard use cases for text based long context include:

Summarizing large corpuses of text
Previous summarization options with smaller context models would require a sliding window or another technique to keep state of previous sections as new tokens are passed to the model
Question and answering
Historically this was only possible with RAG given the limited amount of context and models' factual recall being low
Agentic workflows
Text is the underpinning of how agents keep state of what they have done and what they need to do; not having enough information about the world and the agent's goal is a limitation on the reliability of agents
Many-shot in-context learning is one of the most unique capabilities unlocked by long context models. Research has shown that taking the common "single shot" or "multi-shot" example paradigm, where the model is presented with one or a few examples of a task, and scaling that up to hundreds, thousands, or even hundreds of thousands of examples, can lead to novel model capabilities. This many-shot approach has also been shown to perform similarly to models which were fine-tuned for a specific task. For use cases where a Gemini model's performance is not yet sufficient for a production rollout, you can try the many-shot approach. As you might explore later in the long context optimization section, context caching makes this type of high input token workload much more economically feasible and even lower latency in some cases.

Long form video
Video content's utility has long been constrained by the lack of accessibility of the medium itself. It was hard to skim the content, transcripts often failed to capture the nuance of a video, and most tools don't process image, text, and audio together. With Gemini 1.5, the long-context text capabilities translate to the ability to reason and answer questions about multimodal inputs with sustained performance. Gemini 1.5 Flash, when tested on the needle in a video haystack problem with 1M tokens, obtained >99.8% recall of the video in the context window, and 1.5 Pro reached state of the art performance on the Video-MME benchmark.

Some emerging and standard use cases for video long context include:

Video question and answering
Video memory, as shown with Google's Project Astra
Video captioning
Video recommendation systems, by enriching existing metadata with new multimodal understanding
Video customization, by looking at a corpus of data and associated video metadata and then removing parts of videos that are not relevant to the viewer
Video content moderation
Real-time video processing
When working with videos, it is important to consider how the videos are processed into tokens, which affects billing and usage limits. You can learn more about prompting with video files in the Prompting guide.

Long form audio
The Gemini 1.5 models were the first natively multimodal large language models that could understand audio. Historically, the typical developer workflow would involve stringing together multiple domain specific models, like a speech-to-text model and a text-to-text model, in order to process audio. This led to additional latency required by performing multiple round-trip requests and decreased performance usually attributed to disconnected architectures of the multiple model setup.

On standard audio-haystack evaluations, Gemini 1.5 Pro is able to find the hidden audio in 100% of the tests and Gemini 1.5 Flash is able to find it in 98.7% of the tests. Gemini 1.5 Flash accepts up to 9.5 hours of audio in a single request and Gemini 1.5 Pro can accept up to 19 hours of audio using the 2-million-token context window. Further, on a test set of 15-minute audio clips, Gemini 1.5 Pro archives a word error rate (WER) of ~5.5%, much lower than even specialized speech-to-text models, without the added complexity of extra input segmentation and pre-processing.

Some emerging and standard use cases for audio context include:

Real-time transcription and translation
Podcast / video question and answering
Meeting transcription and summarization
Voice assistants
You can learn more about prompting with audio files in the Prompting guide.

Long context optimizations
The primary optimization when working with long context and the Gemini 1.5 models is to use context caching. Beyond the previous impossibility of processing lots of tokens in a single request, the other main constraint was the cost. If you have a "chat with your data" app where a user uploads 10 PDFs, a video, and some work documents, you would historically have to work with a more complex retrieval augmented generation (RAG) tool / framework in order to process these requests and pay a significant amount for tokens moved into the context window. Now, you can cache the files the user uploads and pay to store them on a per hour basis. The input / output cost per request with Gemini 1.5 Flash for example is ~4x less than the standard input / output cost, so if the user chats with their data enough, it becomes a huge cost saving for you as the developer.

Long context limitations
In various sections of this guide, we talked about how Gemini 1.5 models achieve high performance across various needle-in-a-haystack retrieval evals. These tests consider the most basic setup, where you have a single needle you are looking for. In cases where you might have multiple "needles" or specific pieces of information you are looking for, the model does not perform with the same accuracy. Performance can vary to a wide degree depending on the context. This is important to consider as there is an inherent tradeoff between getting the right information retrieved and cost. You can get ~99% on a single query, but you have to pay the input token cost every time you send that query. So for 100 pieces of information to be retrieved, if you needed 99% performance, you would likely need to send 100 requests. This is a good example of where context caching can significantly reduce the cost associated with using Gemini models while keeping the performance high.

**Gemini thinking**

The Gemini 2.5 series models use an internal "thinking process" during response generation. This process contributes to their improved reasoning capabilities and helps them use multi-step planning to solve complex tasks. This makes these models especially good at coding, advanced mathematics, data analysis, and other tasks that require planning or thinking.

Try Gemini 2.5 Flash Preview in Google AI Studio
This guide shows you how to work with Gemini's thinking capabilities using the Gemini API.

***Use thinking models***

Models with thinking capabilities are available in Google AI Studio and through the Gemini API. Thinking is on by default in both the API and AI Studio because the 2.5 series models have the ability to automatically decide when and how much to think based on the prompt. For most use cases, it's beneficial to leave thinking on. But if you want to to turn thinking off, you can do so by setting the thinkingBudget parameter to 0.

Send a basic request

```python
from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")
prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."
response = client.models.generate_content(
    model="gemini-2.5-flash-preview-04-17",
    contents=prompt
)

print(response.text)
```

Set budget on thinking models

The thinkingBudget parameter gives the model guidance on the number of thinking tokens it can use when generating a response. A greater number of tokens is typically associated with more detailed thinking, which is needed for solving more complex tasks. thinkingBudget must be an integer in the range 0 to 24576. Setting the thinking budget to 0 disables thinking.

Depending on the prompt, the model might overflow or underflow the token budget.

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-04-17",
    contents="Explain the Occam's Razor concept and provide everyday examples of it",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)
    ),
)

print(response.text)
```

Use tools with thinking models
Thinking models can use tools to perform actions beyond generating text. This allows them to interact with external systems, execute code, or access real-time information, incorporating the results into their reasoning and final response.

Search Tool
The Search tool allows the model to query external search engines to find up-to-date information or information beyond its training data. This is useful for questions about recent events or highly specific topics.

To configure the search tool, see Configure the Search tool.

Prompt:

What were the major scientific breakthroughs announced last week?
Response (using Search Tool):

Based on recent search results, here are some highlights from the past week in science:

...
Code Execution
The Code execution tool enables the model to generate and run Python code to perform calculations, manipulate data, or solve problems that are best handled algorithmically. The model receives the code's output and can use it in its response.

To configure code execution, see Enable code execution on the model.

Prompt:

What is the sum of the first 50 prime numbers?
Generate and run Python code for the calculation, and make sure you get all 50.
Provide the final sum clearly.
Response (using Code Execution Tool):

Okay, I can calculate that. I will generate Python code to find the first 50 prime numbers and sum them up.

```python
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

primes = []
num = 2
while len(primes) < 50:
    if is_prime(num):
        primes.append(num)
    num += 1

total_sum = sum(primes)
print(total_sum)
```

Running the code...

Code Execution Result:
Outcome: OK
Output:

5117
Use code with caution.
The sum of the first 50 prime numbers is 5117.
Thinking with structured output
With structured output, you can constrain Gemini to respond with JSON, a structured output format suitable for automated processing. This is particularly useful for integrating the model's output into applications.

You can specify the format directly in the prompt or supply a schema through model configuration.

Prompt:

Provide a list of 3 famous physicists and their key contributions
in JSON format.
Use this JSON schema:

Physicist = {'name': str, 'contribution': str, 'era': str}
Return: list[Physicist]
Response (instructed for JSON):

```json
[
{
"name": "Albert Einstein",
"contribution": "Theory of Relativity (Special and General)",
"era": "Early 20th Century"
},
{
"name": "Isaac Newton",
"contribution": "Laws of Motion and Universal Gravitation",
"era": "Late 17th / Early 18th Century"
},
{
"name": "Marie Curie",
"contribution": "Pioneering research on radioactivity",
"era": "Late 19th / Early 20th Century"
}
]
```

**Document understanding**

Python

The Gemini API supports PDF input, including long documents (up to 3600 pages). Gemini models process PDFs with native vision, and are therefore able to understand both text and image contents inside documents. With native PDF vision support, Gemini models are able to:

Analyze diagrams, charts, and tables inside documents
Extract information into structured output formats
Answer questions about visual and text contents in documents
Summarize documents
Transcribe document content (e.g. to HTML) preserving layouts and formatting, for use in downstream applications
This tutorial demonstrates some possible ways to use the Gemini API to process PDF documents.

***PDF input***

For PDF payloads under 20MB, you can choose between uploading base64 encoded documents or directly uploading locally stored files.

As inline data
You can process PDF documents directly from URLs. Here's a code snippet showing how to do this:

```python
from google import genai
from google.genai import types
import httpx

client = genai.Client()

doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"

# Retrieve and encode the PDF byte
doc_data = httpx.get(doc_url).content

prompt = "Summarize this document"
response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[
      types.Part.from_bytes(
        data=doc_data,
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)
```

***Technical details***

Gemini 2.5 Pro and 2.5 Flash support a maximum of 3,600 document pages. Document pages must be in one of the following text data MIME types:

PDF - application/pdf
JavaScript - application/x-javascript, text/javascript
Python - application/x-python, text/x-python
TXT - text/plain
HTML - text/html
CSS - text/css
Markdown - text/md
CSV - text/csv
XML - text/xml
RTF - text/rtf

Each document page is equivalent to 258 tokens.

While there are no specific limits to the number of pixels in a document besides the model's context window, larger pages are scaled down to a maximum resolution of 3072x3072 while preserving their original aspect ratio, while smaller pages are scaled up to 768x768 pixels. There is no cost reduction for pages at lower sizes, other than bandwidth, or performance improvement for pages at higher resolution.

For best results:

Rotate pages to the correct orientation before uploading.
Avoid blurry pages.
If using a single page, place the text prompt after the page.

***Locally stored PDFs***

For locally stored PDFs, you can use the following approach:

```python
from google import genai
from google.genai import types
import pathlib
import httpx

client = genai.Client()

doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"

# Retrieve and encode the PDF byte
filepath = pathlib.Path('file.pdf')
filepath.write_bytes(httpx.get(doc_url).content)

prompt = "Summarize this document"
response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)
```

***Large PDFs***

You can use the File API to upload a document of any size. Always use the File API when the total request size (including the files, text prompt, system instructions, etc.) is larger than 20 MB.

Note: The File API lets you store up to 20 GB of files per project, with a per-file maximum size of 2 GB. Files are stored for 48 hours. They can be accessed in that period with your API key, but cannot be downloaded from the API. The File API is available at no cost in all regions where the Gemini API is available.
Call media.upload to upload a file using the File API. The following code uploads a document file and then uses the file in a call to models.generateContent.

***Large PDFs from URLs***

Use the File API for large PDF files available from URLs, simplifying the process of uploading and processing these documents directly through their URLs:

```python
from google import genai
from google.genai import types
import io
import httpx

client = genai.Client()

long_context_pdf_path = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"

# Retrieve and upload the PDF using the File API
doc_io = io.BytesIO(httpx.get(long_context_pdf_path).content)

sample_doc = client.files.upload(
  # You can pass a path or a file-like object here
  file=doc_io,
  config=dict(
    mime_type='application/pdf')
)

prompt = "Summarize this document"

response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[sample_doc, prompt])
print(response.text)
```

***Large PDFs stored locally***

```python
from google import genai
from google.genai import types
import pathlib
import httpx

client = genai.Client()

long_context_pdf_path = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"

# Retrieve the PDF
file_path = pathlib.Path('A17.pdf')
file_path.write_bytes(httpx.get(long_context_pdf_path).content)

# Upload the PDF using the File API
sample_file = client.files.upload(
  file=file_path,
)

prompt="Summarize this document"

response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[sample_file, "Summarize this document"])
print(response.text)
```

You can verify the API successfully stored the uploaded file and get its metadata by calling files.get. Only the name (and by extension, the uri) are unique.

```python
from google import genai
import pathlib

client = genai.Client()

fpath = pathlib.Path('example.txt')
fpath.write_text('hello')

file = client.files.upload('example.txt')

file_info = client.files.get(file.name)
print(file_info.model_dump_json(indent=4))
```

***Multiple PDFs***

The Gemini API is capable of processing multiple PDF documents in a single request, as long as the combined size of the documents and the text prompt stays within the model's context window.

```python
from google import genai
import io
import httpx

client = genai.Client()

doc_url_1 = "https://arxiv.org/pdf/2312.11805"
doc_url_2 = "https://arxiv.org/pdf/2403.05530"

# Retrieve and upload both PDFs using the File API
doc_data_1 = io.BytesIO(httpx.get(doc_url_1).content)
doc_data_2 = io.BytesIO(httpx.get(doc_url_2).content)

sample_pdf_1 = client.files.upload(
  file=doc_data_1,
  config=dict(mime_type='application/pdf')
)
sample_pdf_2 = client.files.upload(
  file=doc_data_2,
  config=dict(mime_type='application/pdf')
)

prompt = "What is the difference between each of the main benchmarks between these two papers? Output these in a table."

response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[sample_pdf_1, sample_pdf_2, prompt])
print(response.text)
```

**Image understanding**

Gemini models can process images, enabling many frontier developer use cases that would have historically required domain specific models. Some of Gemini's vision capabilities include the ability to:

Caption and answer questions about images
Transcribe and reason over PDFs, including up to 2 million tokens
Detect objects in an image and return bounding box coordinates for them
Segment objects within an image
Gemini was built to be multimodal from the ground up and we continue to push the frontier of what is possible. This guide shows how to use the Gemini API to generate text responses based on image inputs and perform common image understanding tasks.

Before you begin
Before calling the Gemini API, ensure you have your SDK of choice installed, and a Gemini API key configured and ready to use.

***Image input***

You can provide images as input to Gemini in the following ways:

Upload an image file using the File API before making a request to generateContent. Use this method for files larger than 20MB or when you want to reuse the file across multiple requests.
Pass inline image data with the request to generateContent. Use this method for smaller files (<20MB total request size) or images fetched directly from URLs.

***Upload an image file***

You can use the Files API to upload an image file. Always use the Files API when the total request size (including the file, text prompt, system instructions, etc.) is larger than 20 MB, or if you intend to use the same image in multiple prompts.

The following code uploads an image file and then uses the file in a call to generateContent.

```python
from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.jpg")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[myfile, "Caption this image."])

print(response.text)
```
To learn more about working with media files, see Files API.

***Pass image data inline***

Instead of uploading an image file, you can pass inline image data in the request to generateContent. This is suitable for smaller images (less than 20MB total request size) or images fetched directly from URLs.

You can provide image data as Base64 encoded strings or by reading local files directly (depending on the SDK).

Local image file:

```python
from google.genai import types

with open('path/to/small-sample.jpg', 'rb') as f:
    img_bytes = f.read()

  response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=[
      types.Part.from_bytes(
        data=img_bytes,
        mime_type='image/jpeg',
      ),
      'Caption this image.'
    ]
  )

  print(response.text)
```
Image from URL:

```python
from google import genai
from google.genai import types

import requests

image_path = "https://goo.gle/instrument-img"
image = requests.get(image_path)

client = genai.Client(api_key="GOOGLE_API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=["What is this image?",
              types.Part.from_bytes(data=image.content, mime_type="image/jpeg")])

print(response.text)
```
A few things to keep in mind about inline image data:

The maximum total request size is 20 MB, which includes text prompts, system instructions, and all files provided inline. If your file's size will make the total request size exceed 20 MB, then use the Files API to upload an image file for use in the request.
If you're using an image sample multiple times, it's more efficient to upload an image file using the File API.

***Prompting with multiple images***

You can provide multiple images in a single prompt by including multiple image Part objects in the contents array. These can be a mix of inline data (local files or URLs) and File API references.

```python

from google import genai
from google.genai import types

client = genai.Client(api_key="GOOGLE_API_KEY")

# Upload the first image
image1_path = "path/to/image1.jpg"
uploaded_file = client.files.upload(file=image1_path)

# Prepare the second image as inline data
image2_path = "path/to/image2.png"
with open(image2_path, 'rb') as f:
    img2_bytes = f.read()

# Create the prompt with text and multiple images
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        "What is different between these two images?",
        uploaded_file,  # Use the uploaded file reference
        types.Part.from_bytes(
            data=img2_bytes,
            mime_type='image/png'
        )
    ]
)

print(response.text)
```

***Get a bounding box for an object***

Gemini models are trained to identify objects in an image and provide their bounding box coordinates. The coordinates are returned relative to the image dimensions, scaled to [0, 1000]. You need to descale these coordinates based on your original image size.

```python
prompt = "Detect the all of the prominent items in the image. The box_2d should be [ymin, xmin, ymax, xmax] normalized to 0-1000."
```
You can use bounding boxes for object detection and localization within images and video. By accurately identifying and delineating objects with bounding boxes, you can unlock a wide range of applications and enhance the intelligence of your projects.

Key benefits
Simple: Integrate object detection capabilities into your applications with ease, regardless of your computer vision expertise.
Customizable: Produce bounding boxes based on custom instructions (e.g. "I want to see bounding boxes of all the green objects in this image"), without having to train a custom model.
Technical details
Input: Your prompt and associated images or video frames.
Output: Bounding boxes in the [y_min, x_min, y_max, x_max] format. The top left corner is the origin. The x and y axis go horizontally and vertically, respectively. Coordinate values are normalized to 0-1000 for every image.
Visualization: AI Studio users will see bounding boxes plotted within the UI.
For Python developers, try the 2D spatial understanding notebook or the experimental 3D pointing notebook.

Normalize coordinates
The model returns bounding box coordinates in the format [y_min, x_min, y_max, x_max]. To convert these normalized coordinates to the pixel coordinates of your original image, follow these steps:

Divide each output coordinate by 1000.
Multiply the x-coordinates by the original image width.
Multiply the y-coordinates by the original image height.
To explore more detailed examples of generating bounding box coordinates and visualizing them on images, review the Object Detection cookbook example.

***Image segmentation***

Starting with the Gemini 2.5 models, Gemini models are trained to not only detect items but also segment them and provide a mask of their contours.

The model predicts a JSON list, where each item represents a segmentation mask. Each item has a bounding box ("box_2d") in the format [y0, x0, y1, x1] with normalized coordinates between 0 and 1000, a label ("label") that identifies the object, and finally the segmentation mask inside the bounding box, as base64 encoded png that is a probability map with values between 0 and 255. The mask needs to be resized to match the bounding box dimensions, then binarized at your confidence threshold (127 for the midpoint).

```python
prompt = """
  Give the segmentation masks for the wooden and glass items.
  Output a JSON list of segmentation masks where each entry contains the 2D
  bounding box in the key "box_2d", the segmentation mask in key "mask", and
  the text label in the key "label". Use descriptive labels.
"""
```

A table with cupcakes, with the wooden and glass objects highlighted
Mask of the wooden and glass objects found on the picture
Check the segmentation example in the cookbook guide for a more detailed example.

***Supported image formats***

Gemini supports the following image format MIME types:

PNG - image/png
JPEG - image/jpeg
WEBP - image/webp
HEIC - image/heic
HEIF - image/heif

***Technical details about images***

File limit: Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash, 1.5 Pro, and 1.5 Flash support a maximum of 3,600 image files per request.
Token calculation:
Gemini 1.5 Flash and Gemini 1.5 Pro: 258 tokens if both dimensions <= 384 pixels. Larger images are tiled (min tile 256px, max 768px, resized to 768x768), with each tile costing 258 tokens.
Gemini 2.0 Flash: 258 tokens if both dimensions <= 384 pixels. Larger images are tiled into 768x768 pixel tiles, each costing 258 tokens.
Best practices:
Ensure images are correctly rotated.
Use clear, non-blurry images.
When using a single image with text, place the text prompt after the image part in the contents array.

**Audio understanding**

Gemini can analyze and understand audio input, enabling use cases like the following:

Describe, summarize, or answer questions about audio content.
Provide a transcription of the audio.
Analyze specific segments of the audio.
This guide shows you how to use the Gemini API to generate a text response to audio input.

Before you begin
Before calling the Gemini API, ensure you have your SDK of choice installed, and a Gemini API key configured and ready to use.

***Input audio***

You can provide audio data to Gemini in the following ways:

Upload an audio file before making a request to generateContent.
Pass inline audio data with the request to generateContent.

***Upload an audio file***

You can use the Files API to upload an audio file. Always use the Files API when the total request size (including the files, text prompt, system instructions, etc.) is larger than 20 MB.

The following code uploads an audio file and then uses the file in a call to generateContent.

```python
from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.mp3")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=["Describe this audio clip", myfile]
)

print(response.text)
```

To learn more about working with media files, see Files API.

***Pass audio data inline***

Instead of uploading an audio file, you can pass inline audio data in the request to generateContent:

```python
from google.genai import types

with open('path/to/small-sample.mp3', 'rb') as f:
    audio_bytes = f.read()

response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=[
    'Describe this audio clip',
    types.Part.from_bytes(
      data=audio_bytes,
      mime_type='audio/mp3',
    )
  ]
)

print(response.text)
```

A few things to keep in mind about inline audio data:

The maximum request size is 20 MB, which includes text prompts, system instructions, and files provided inline. If your file's size will make the total request size exceed 20 MB, then use the Files API to upload an audio file for use in the request.
If you're using an audio sample multiple times, it's more efficient to upload an audio file.

***Get a transcript***

To get a transcript of audio data, just ask for it in the prompt:

```python
from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.mp3")
prompt = 'Generate a transcript of the speech.'

response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=[prompt, myfile]
)

print(response.text)
``` 

***Refer to timestamps***

You can refer to specific sections of an audio file using timestamps of the form MM:SS. For example, the following prompt requests a transcript that

Starts at 2 minutes 30 seconds from the beginning of the file.
Ends at 3 minutes 29 seconds from the beginning of the file.

```python
# Create a prompt containing timestamps.
prompt = "Provide a transcript of the speech from 02:30 to 03:29."
```

***Count tokens***

Call the countTokens method to get a count of the number of tokens in an audio file. For example:

```python
response = client.models.count_tokens(
  model='gemini-2.0-flash',
  contents=[myfile]
)

print(response)
```

***Supported audio formats***

Gemini supports the following audio format MIME types:

WAV - audio/wav
MP3 - audio/mp3
AIFF - audio/aiff
AAC - audio/aac
OGG Vorbis - audio/ogg
FLAC - audio/flac

***Technical details about audio***

Gemini represents each second of audio as 32 tokens; for example, one minute of audio is represented as 1,920 tokens.
Gemini can only infer responses to English-language speech.
Gemini can "understand" non-speech components, such as birdsong or sirens.
The maximum supported length of audio data in a single prompt is 9.5 hours. Gemini doesn't limit the number of audio files in a single prompt; however, the total combined length of all audio files in a single prompt can't exceed 9.5 hours.
Gemini downsamples audio files to a 16 Kbps data resolution.
If the audio source contains multiple channels, Gemini combines those channels into a single channel.

***Files API***

You can use the Files API to upload and interact with media files. The Files API lets you store up to 20 GB of files per project, with a per-file maximum size of 2 GB. Files are stored for 48 hours. During that time, you can use the API to get metadata about the files, but you can't download the files. The Files API is available at no cost in all regions where the Gemini API is available.

This guide shows you how to work with media files using the Files API. The basic operations are the same for audio files, images, videos, documents, and other supported file types.

***Upload a file***

You can use the Files API to upload a media file. Always use the Files API when the total request size (including the files, text prompt, system instructions, etc.) is larger than 20 MB.

```python
from google import genai

client = genai.Client(api_key="GOOGLE_API_KEY")

myfile = client.files.upload(file="path/to/sample.mp3")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=["Describe this audio clip", myfile]
)

print(response.text)
```

***Get metadata for a file***

You can verify that the API successfully stored the uploaded file and get its metadata by calling files.get.

```python
myfile = client.files.upload(file='path/to/sample.mp3')
file_name = myfile.name
myfile = client.files.get(name=file_name)
print(myfile)
```

***List uploaded files***

You can upload multiple files using the Files API. The following code gets a list of all the files uploaded:

```python
print('My files:')
for f in client.files.list():
    print(' ', f.name)
```

***Delete uploaded files***

Files are automatically deleted after 48 hours. You can also manually delete an uploaded file:

```python
myfile = client.files.upload(file='path/to/sample.mp3')
client.files.delete(name=myfile.name)
```

***Context caching***


In a typical AI workflow, you might pass the same input tokens over and over to a model. Using the Gemini API context caching feature, you can pass some content to the model once, cache the input tokens, and then refer to the cached tokens for subsequent requests. At certain volumes, using cached tokens is lower cost than passing in the same corpus of tokens repeatedly.

When you cache a set of tokens, you can choose how long you want the cache to exist before the tokens are automatically deleted. This caching duration is called the time to live (TTL). If not set, the TTL defaults to 1 hour. The cost for caching depends on the input token size and how long you want the tokens to persist.

Context caching varies from model to model.

***When to use context caching***

Context caching is particularly well suited to scenarios where a substantial initial context is referenced repeatedly by shorter requests. Consider using context caching for use cases such as:

Chatbots with extensive system instructions
Repetitive analysis of lengthy video files
Recurring queries against large document sets
Frequent code repository analysis or bug fixing
How to use context caching
This section assumes that you've installed a Gemini SDK (or have curl installed) and that you've configured an API key, as shown in the quickstart.

***Generate content using a cache***

The following example shows how to generate content using a cached system instruction and video file.

PDFs

```python
from google import genai
from google.genai import types
import io
import httpx

client = genai.Client()

long_context_pdf_path = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"

# Retrieve and upload the PDF using the File API
doc_io = io.BytesIO(httpx.get(long_context_pdf_path).content)

document = client.files.upload(
  file=doc_io,
  config=dict(mime_type='application/pdf')
)

model_name = "gemini-2.0-flash-001"
system_instruction = "You are an expert analyzing transcripts."

# Create a cached content object
cache = client.caches.create(
    model=model_name,
    config=types.CreateCachedContentConfig(
      system_instruction=system_instruction,
      contents=[document],
    )
)

# Display the cache details
print(f'{cache=}')

# Generate content using the cached prompt and document
response = client.models.generate_content(
  model=model_name,
  contents="Please summarize this transcript",
  config=types.GenerateContentConfig(
    cached_content=cache.name
  ))

# (Optional) Print usage metadata for insights into the API call
print(f'{response.usage_metadata=}')

# Print the generated text
print('\n\n', response.text)
```

***List caches***

It's not possible to retrieve or view cached content, but you can retrieve cache metadata (name, model, display_name, usage_metadata, create_time, update_time, and expire_time).

To list metadata for all uploaded caches, use CachedContent.list():

```python
for cache in client.caches.list():
  print(cache)
```

To fetch the metadata for one cache object, if you know its name, use get:

```python
client.caches.get(name=name)
```
***Update a cache***

You can set a new ttl or expire_time for a cache. Changing anything else about the cache isn't supported.

The following example shows how to update the ttl of a cache using client.caches.update().

```python
from google import genai
from google.genai import types

client.caches.update(
  name = cache.name,
  config  = types.UpdateCachedContentConfig(
      ttl='300s'
  )
)
```
To set the expiry time, it will accepts either a datetime object or an ISO-formatted datetime string (dt.isoformat(), like 2025-01-27T16:02:36.473528+00:00). Your time must include a time zone (datetime.utcnow() doesn't attach a time zone, datetime.now(datetime.timezone.utc) does attach a time zone).

```python
from google import genai
from google.genai import types
import datetime

# You must use a time zone-aware time.
in10min = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)

client.caches.update(
  name = cache.name,
  config  = types.UpdateCachedContentConfig(
      expire_time=in10min
  )
)
```
***Delete a cache***

The caching service provides a delete operation for manually removing content from the cache. The following example shows how to delete a cache:

```python
client.caches.delete(cache.name)
```

***How caching reduces costs***

Context caching is a paid feature designed to reduce overall operational costs. Billing is based on the following factors:

Cache token count: The number of input tokens cached, billed at a reduced rate when included in subsequent prompts.
Storage duration: The amount of time cached tokens are stored (TTL), billed based on the TTL duration of cached token count. There are no minimum or maximum bounds on the TTL.
Other factors: Other charges apply, such as for non-cached input tokens and output tokens.
For up-to-date pricing details, refer to the Gemini API pricing page. To learn how to count tokens, see the Token guide.

***Additional considerations***

Keep the following considerations in mind when using context caching:

The minimum input token count for context caching is 4,096, and the maximum is the same as the maximum for the given model. (For more on counting tokens, see the Token guide).
The model doesn't make any distinction between cached tokens and regular input tokens. Cached content is a prefix to the prompt.
There are no special rate or usage limits on context caching; the standard rate limits for GenerateContent apply, and token limits include cached tokens.
The number of cached tokens is returned in the usage_metadata from the create, get, and list operations of the cache service, and also in GenerateContent when using the cache.

Google Gen AI SDK
=================

|pypi|

`<https://github.com/googleapis/python-genai>`_

.. |pypi| image:: https://img.shields.io/pypi/v/google-genai.svg
   :target: https://pypi.org/project/google-genai/

:strong:`google-genai` is an initial Python client library for interacting with
Google's Generative AI APIs.

Google Gen AI Python SDK provides an interface for developers to integrate Google's generative models into their Python applications. It supports the `Gemini Developer API <https://ai.google.dev/gemini-api/docs>`_ and `Vertex AI <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview>`_ APIs.

Installation
------------

.. code:: shell

    pip install google-genai

Imports
-------

.. code:: python

    from google import genai
    from google.genai import types

Create a client
---------------

Please run one of the following code blocks to create a client for
different services (`Gemini Developer API <https://ai.google.dev/gemini-api/docs>`_ or `Vertex AI <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview>`_). Feel free to switch the client and
run all the examples to see how it behaves under different APIs.

.. code:: python

    # Only run this block for Gemini Developer API
    client = genai.Client(api_key='GEMINI_API_KEY')

.. code:: python

    # Only run this block for Vertex AI API
    client = genai.Client(
        vertexai=True, project='your-project-id', location='us-central1'
    )


**(Optional) Using environment variables:**

You can create a client by configuring the necessary environment variables.
Configuration setup instructions depends on whether you're using the Gemini
Developer API or the Gemini API in Vertex AI.

**Gemini Developer API:** Set `GOOGLE_API_KEY` as shown below:

.. code:: bash

    export GOOGLE_API_KEY='your-api-key'


**Gemini API in Vertex AI:** Set `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`
and `GOOGLE_CLOUD_LOCATION`, as shown below:

.. code:: bash

    export GOOGLE_GENAI_USE_VERTEXAI=true
    export GOOGLE_CLOUD_PROJECT='your-project-id'
    export GOOGLE_CLOUD_LOCATION='us-central1'


.. code:: python

    client = genai.Client()


API Selection
^^^^^^^^^^^^^

By default, the SDK uses the beta API endpoints provided by Google to support preview features in the APIs. The stable API endpoints can be selected by setting the API version to `v1`.

To set the API version use ``http_options``. For example, to set the API version to ``v1`` for Vertex AI:

.. code:: python

    client = genai.Client(
        vertexai=True,
        project='your-project-id',
        location='us-central1',
        http_options=types.HttpOptions(api_version='v1')
    )

To set the API version to `v1alpha` for the Gemini Developer API:

.. code:: python

    # Only run this block for Gemini Developer API
    client = genai.Client(
        api_key='GEMINI_API_KEY',
        http_options=types.HttpOptions(api_version='v1alpha')
    )


Types
-----

Parameter types can be specified as either dictionaries(``TypedDict``) or `Pydantic Models <https://pydantic.readthedocs.io/en/stable/model.html>`_.
Pydantic model types are available in the ``types`` module.

Models
======

The ``client.models`` modules exposes model inferencing and model
getters.

Generate Content
----------------

with text content
^^^^^^^^^^^^^^^^^

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001', contents='Why is the sky blue?'
    )
    print(response.text)

with uploaded file (Gemini Developer API only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

download the file in console.

.. code:: console

    !wget -q https://storage.googleapis.com/generativeai-downloads/data/a11.txt

python code.

.. code:: python

    file = client.files.upload(file='a11.txt')
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=['Could you summarize this file?', file]
    )
    print(response.text)


How to structure `contents` argument for `generate_content`
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The SDK always converts the inputs to the `contents` argument into
`list[types.Content]`.
The following shows some common ways to provide your inputs.

Provide a `list[types.Content]`
""""""""""""""""""""""""""""""
This is the canonical way to provide contents, SDK will not do any conversion.

Provide a `types.Content` instance
""""""""""""""""""""""""""""""

.. code:: python

    contents = types.Content(
    role='user',
    parts=[types.Part.from_text(text='Why is the sky blue?')]
    )

SDK converts this to

.. code:: python

    [
    types.Content(
        role='user',
        parts=[types.Part.from_text(text='Why is the sky blue?')]
    )
    ]

Provide a string
""""""""""""""""""

.. code:: python

    contents='Why is the sky blue?'

The SDK will assume this is a text part, and it converts this into the following:

.. code:: python

    [
    types.UserContent(
        parts=[
        types.Part.from_text(text='Why is the sky blue?')
        ]
    )
    ]

Where a `types.UserContent` is a subclass of `types.Content`, it sets the
`role` field to be `user`.

Provide a list of string
""""""""""""""""""""""""

.. code:: python
    contents=['Why is the sky blue?', 'Why is the cloud white?']

The SDK assumes these are 2 text parts, it converts this into a single content,
like the following:

.. code:: python

    [
    types.UserContent(
        parts=[
        types.Part.from_text(text='Why is the sky blue?'),
        types.Part.from_text(text='Why is the cloud white?'),
        ]
    )
    ]

Where a `types.UserContent` is a subclass of `types.Content`, the
`role` field in `types.UserContent` is fixed to be `user`.

Provide a function call part
""""""""""""""""""""""""""

.. code:: python

    contents = types.Part.from_function_call(
    name='get_weather_by_location',
    args={'location': 'Boston'}
    )

The SDK converts a function call part to a content with a `model` role:

.. code:: python

    [
    types.ModelContent(
        parts=[
        types.Part.from_function_call(
            name='get_weather_by_location',
            args={'location': 'Boston'}
        )
        ]
    )
    ]

Where a `types.ModelContent` is a subclass of `types.Content`, the
`role` field in `types.ModelContent` is fixed to be `model`.

Provide a list of function call parts
""""""""""""""""""""""""""""""

.. code:: python

    contents = [
    types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'Boston'}
    ),
    types.Part.from_function_call(
        name='get_weather_by_location',
        args={'location': 'New York'}
    ),
    ]

The SDK converts a list of function call parts to the a content with a `model` role:

.. code:: python

    [
    types.ModelContent(
        parts=[
        types.Part.from_function_call(
            name='get_weather_by_location',
            args={'location': 'Boston'}
        ),
        types.Part.from_function_call(
            name='get_weather_by_location',
            args={'location': 'New York'}
        )
        ]
    )
    ]

Where a `types.ModelContent` is a subclass of `types.Content`, the
`role` field in `types.ModelContent` is fixed to be `model`.

Provide a non function call part
""""""""""""""""""""""""

.. code:: python

    contents = types.Part.from_uri(
    file_uri: 'gs://generativeai-downloads/images/scones.jpg',
    mime_type: 'image/jpeg',
    )

The SDK converts all non function call parts into a content with a `user` role.

.. code:: python

    [
    types.UserContent(parts=[
        types.Part.from_uri(
        file_uri: 'gs://generativeai-downloads/images/scones.jpg',
        mime_type: 'image/jpeg',
        )
    ])
    ]

Provide a list of non function call parts
""""""""""""""""""""

.. code:: python

    contents = [
    types.Part.from_text('What is this image about?'),
    types.Part.from_uri(
        file_uri: 'gs://generativeai-downloads/images/scones.jpg',
        mime_type: 'image/jpeg',
    )
    ]

The SDK will convert the list of parts into a content with a `user` role

.. code:: python

    [
    types.UserContent(
        parts=[
        types.Part.from_text('What is this image about?'),
        types.Part.from_uri(
            file_uri: 'gs://generativeai-downloads/images/scones.jpg',
            mime_type: 'image/jpeg',
        )
        ]
    )
    ]

Mix types in contents
""""""""""""""""""""""""""
You can also provide a list of `types.ContentUnion`. The SDK leaves items of
`types.Content` as is, it groups consecutive non function call parts into a
single `types.UserContent`, and it groups consecutive function call parts into
a single `types.ModelContent`.

If you put a list within a list, the inner list can only contain
`types.PartUnion` items. The SDK will convert the inner list into a single
`types.UserContent`.


System Instructions and Other Configs
-------------------------------------

The output of the model can be influenced by several optional settings
available in generate_content's config parameter. For example, the
variability and length of the output can be influenced by the temperature
and max_output_tokens respectively.

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='high',
        config=types.GenerateContentConfig(
            system_instruction='I say high, you say low',
            max_output_tokens=3,
            temperature=0.3,
        ),
    )
    print(response.text)

Typed Config
------------

All API methods support Pydantic types for parameters as well as
dictionaries. You can get the type from ``google.genai.types``.

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=types.Part.from_text(text='Why is the sky blue?'),
        config=types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            top_k=20,
            candidate_count=1,
            seed=5,
            max_output_tokens=100,
            stop_sequences=['STOP!'],
            presence_penalty=0.0,
            frequency_penalty=0.0,
        ),
    )

    print(response.text)

List Base Models
----------------

To retrieve tuned models, see: :ref:`List Tuned Models`

.. code:: python

    for model in client.models.list():
        print(model)

.. code:: python

    pager = client.models.list(config={'page_size': 10})
    print(pager.page_size)
    print(pager[0])
    pager.next_page()
    print(pager[0])

Async
~~~~~

.. code:: python

    async for job in await client.aio.models.list():
        print(job)

.. code:: python

    async_pager = await client.aio.models.list(config={'page_size': 10})
    print(async_pager.page_size)
    print(async_pager[0])
    await async_pager.next_page()
    print(async_pager[0])

Safety Settings
---------------

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Say something bad.',
        config=types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(
                    category='HARM_CATEGORY_HATE_SPEECH',
                    threshold='BLOCK_ONLY_HIGH',
                )
            ]
        ),
    )
    print(response.text)

Function Calling
----------------

Automatic Python function Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass a Python function directly and it will be automatically
called and responded.

.. code:: python

    def get_current_weather(location: str) -> str:
        """Returns the current weather.

        Args:
          location: The city and state, e.g. San Francisco, CA
        """
        return 'sunny'


    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='What is the weather like in Boston?',
        config=types.GenerateContentConfig(
            tools=[get_current_weather],
        ),
    )

    print(response.text)

Disabling automatic function calling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you pass in a python function as a tool directly, and do not want
automatic function calling, you can disable automatic function calling
as follows:

.. code:: python
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='What is the weather like in Boston?',
        config=types.GenerateContentConfig(
            tools=[get_current_weather],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

With automatic function calling disabled, you will get a list of function call
parts in the response:

.. code:: python
    function_calls: Optional[List[types.FunctionCall]] = response.function_calls


Manually declare and invoke a function for function calling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't want to use the automatic function support, you can manually
declare the function and invoke it.

The following example shows how to declare a function and pass it as a tool.
Then you will receive a function call part in the response.

.. code:: python

    function = types.FunctionDeclaration(
        name='get_current_weather',
        description='Get the current weather in a given location',
        parameters=types.Schema(
            type='OBJECT',
            properties={
                'location': types.Schema(
                    type='STRING',
                    description='The city and state, e.g. San Francisco, CA',
                ),
            },
            required=['location'],
        ),
    )

    tool = types.Tool(function_declarations=[function])

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='What is the weather like in Boston?',
        config=types.GenerateContentConfig(
            tools=[tool],
        ),
    )
    print(response.function_calls[0])

After you receive the function call part from the model, you can invoke the function
and get the function response. And then you can pass the function response to
the model.
The following example shows how to do it for a simple function invocation.

.. code:: python

    user_prompt_content = types.Content(
        role='user',
        parts=[types.Part.from_text(text='What is the weather like in Boston?')],
    )
    function_call_part = response.function_calls[0]
    function_call_content = response.candidates[0].content


    try:
        function_result = get_current_weather(
            **function_call_part.function_call.args
        )
        function_response = {'result': function_result}
    except (
        Exception
    ) as e:  # instead of raising the exception, you can let the model handle it
        function_response = {'error': str(e)}


    function_response_part = types.Part.from_function_response(
        name=function_call_part.name,
        response=function_response,
    )
    function_response_content = types.Content(
        role='tool', parts=[function_response_part]
    )

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=[
            user_prompt_content,
            function_call_content,
            function_response_content,
        ],
        config=types.GenerateContentConfig(
            tools=[tool],
        ),
    )

    print(response.text)


Function calling with ``ANY`` tools config mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you configure function calling mode to be `ANY`, then the model will always
return function call parts. If you also pass a python function as a tool, by
default the SDK will perform automatic function calling until the remote calls
exceed the maximum remote call for automatic function calling (default to 10 times).

If you'd like to disable automatic function calling in `ANY` mode:

.. code-block:: python

    def get_current_weather(location: str) -> str:
        """Returns the current weather.

        Args:
            location: The city and state, e.g. San Francisco, CA
        """
        return "sunny"

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents="What is the weather like in Boston?",
        config=types.GenerateContentConfig(
            tools=[get_current_weather],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode='ANY')
            ),
        ),
    )

If you'd like to set ``x`` number of automatic function call turns, you can
configure the maximum remote calls to be ``x + 1``.
Assuming you prefer ``1`` turn for automatic function calling:

.. code-block:: python

    def get_current_weather(location: str) -> str:
        """Returns the current weather.

        Args:
            location: The city and state, e.g. San Francisco, CA
        """
        return "sunny"

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents="What is the weather like in Boston?",
        config=types.GenerateContentConfig(
            tools=[get_current_weather],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=2
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode='ANY')
            ),
        ),
    )

JSON Response Schema
--------------------

Pydantic Model Schema support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Schemas can be provided as Pydantic Models.

.. code:: python

    from pydantic import BaseModel


    class CountryInfo(BaseModel):
        name: str
        population: int
        capital: str
        continent: str
        gdp: int
        official_language: str
        total_area_sq_mi: int


    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Give me information for the United States.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=CountryInfo,
        ),
    )
    print(response.text)

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Give me information for the United States.',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema={
                'required': [
                    'name',
                    'population',
                    'capital',
                    'continent',
                    'gdp',
                    'official_language',
                    'total_area_sq_mi',
                ],
                'properties': {
                    'name': {'type': 'STRING'},
                    'population': {'type': 'INTEGER'},
                    'capital': {'type': 'STRING'},
                    'continent': {'type': 'STRING'},
                    'gdp': {'type': 'INTEGER'},
                    'official_language': {'type': 'STRING'},
                    'total_area_sq_mi': {'type': 'INTEGER'},
                },
                'type': 'OBJECT',
            },
        ),
    )
    print(response.text)

Enum Response Schema
--------------------

Text Response
~~~~~~~~~~~~~

You can set response_mime_type to 'text/x.enum' to return one of those enum 
values as the response.

.. code:: python

    from enum import Enum

    class InstrumentEnum(Enum):
        PERCUSSION = 'Percussion'
        STRING = 'String'
        WOODWIND = 'Woodwind'
        BRASS = 'Brass'
        KEYBOARD = 'Keyboard'

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='What instrument plays multiple notes at once?',
        config={
            'response_mime_type': 'text/x.enum',
            'response_schema': InstrumentEnum,
        },
    )
    print(response.text)

JSON Response
~~~~~~~~~~~~~

You can also set response_mime_type to 'application/json', the response will be 
identical but in quotes.

.. code:: python

    class InstrumentEnum(Enum):
        PERCUSSION = 'Percussion'
        STRING = 'String'
        WOODWIND = 'Woodwind'
        BRASS = 'Brass'
        KEYBOARD = 'Keyboard'

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='What instrument plays multiple notes at once?',
        config={
            'response_mime_type': 'application/json',
            'response_schema': InstrumentEnum,
        },
    )
    print(response.text)

Streaming
---------

Streaming for text content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    for chunk in client.models.generate_content_stream(
        model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
    ):
        print(chunk.text, end='')

Streaming for image content
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your image is stored in `Google Cloud Storage <https://cloud.google.com/storage>`_, you can use the `from_uri` class method to create a `Part` object.

.. code:: python

    for chunk in client.models.generate_content_stream(
        model='gemini-2.0-flash-001',
        contents=[
            'What is this image about?',
            types.Part.from_uri(
                file_uri='gs://generativeai-downloads/images/scones.jpg',
                mime_type='image/jpeg',
            ),
        ],
    ):
        print(chunk.text, end='')


If your image is stored in your local file system, you can read it in as bytes
data and use the ``from_bytes`` class method to create a ``Part`` object.

.. code:: python

    YOUR_IMAGE_PATH = 'your_image_path'
    YOUR_IMAGE_MIME_TYPE = 'your_image_mime_type'
    with open(YOUR_IMAGE_PATH, 'rb') as f:
        image_bytes = f.read()

    for chunk in client.models.generate_content_stream(
        model='gemini-2.0-flash-001',
        contents=[
            'What is this image about?',
            types.Part.from_bytes(data=image_bytes, mime_type=YOUR_IMAGE_MIME_TYPE),
        ],
    ):
        print(chunk.text, end='')

Async
-----

``client.aio`` exposes all the analogous `async methods <https://docs.python.org/3/library/asyncio.html>`_ that are available on ``client``

For example, ``client.aio.models.generate_content`` is the ``async`` version of ``client.models.generate_content``

.. code:: python

    response = await client.aio.models.generate_content(
        model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
    )

    print(response.text)

Streaming
---------

.. code:: python

    async for chunk in await client.aio.models.generate_content_stream(
        model='gemini-2.0-flash-001', contents='Tell me a story in 300 words.'
    ):
        print(chunk.text, end='')

Count Tokens and Compute Tokens
-------------------------------

.. code:: python

    response = client.models.count_tokens(
        model='gemini-2.0-flash-001',
        contents='why is the sky blue?',
    )
    print(response)

Compute Tokens
~~~~~~~~~~~~~~

Compute tokens is only supported in Vertex AI.

.. code:: python

    response = client.models.compute_tokens(
        model='gemini-2.0-flash-001',
        contents='why is the sky blue?',
    )
    print(response)

Async
^^^^^

.. code:: python

    response = await client.aio.models.count_tokens(
        model='gemini-2.0-flash-001',
        contents='why is the sky blue?',
    )
    print(response)

Embed Content
-------------

.. code:: python

    response = client.models.embed_content(
        model='text-embedding-004',
        contents='why is the sky blue?',
    )
    print(response)

.. code:: python

    # multiple contents with config
    response = client.models.embed_content(
        model='text-embedding-004',
        contents=['why is the sky blue?', 'What is your age?'],
        config=types.EmbedContentConfig(output_dimensionality=10),
    )

    print(response)

Imagen
------

Generate Image
~~~~~~~~~~~~~~

Support for generate image in Gemini Developer API is behind an allowlist

.. code:: python

    # Generate Image
    response1 = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='An umbrella in the foreground, and a rainy night sky in the background',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/jpeg',
        ),
    )
    response1.generated_images[0].image.show()

Upscale Image
~~~~~~~~~~~~~

Upscale image is only supported in Vertex AI.

.. code:: python

    # Upscale the generated image from above
    response2 = client.models.upscale_image(
        model='imagen-3.0-generate-002',
        image=response1.generated_images[0].image,
        upscale_factor='x2',
        config=types.UpscaleImageConfig(
            include_rai_reason=True,
            output_mime_type='image/jpeg',
        ),
    )
    response2.generated_images[0].image.show()

Edit Image
~~~~~~~~~~

Edit image uses a separate model from generate and upscale.

Edit image is only supported in Vertex AI.

.. code:: python

    # Edit the generated image from above
    from google.genai.types import RawReferenceImage, MaskReferenceImage

    raw_ref_image = RawReferenceImage(
        reference_id=1,
        reference_image=response1.generated_images[0].image,
    )

    # Model computes a mask of the background
    mask_ref_image = MaskReferenceImage(
        reference_id=2,
        config=types.MaskReferenceConfig(
            mask_mode='MASK_MODE_BACKGROUND',
            mask_dilation=0,
        ),
    )

    response3 = client.models.edit_image(
        model='imagen-3.0-capability-001',
        prompt='Sunlight and clear sky',
        reference_images=[raw_ref_image, mask_ref_image],
        config=types.EditImageConfig(
            edit_mode='EDIT_MODE_INPAINT_INSERTION',
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/jpeg',
        ),
    )
    response3.generated_images[0].image.show()

Veo
------

Generate Videos
~~~~~~~~~~~~~~

Support for generate videos in Vertex and Gemini Developer API is behind an allowlist

.. code:: python

    # Create operation
    operation = client.models.generate_videos(
        model='veo-2.0-generate-001',
        prompt='A neon hologram of a cat driving at top speed',
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            fps=24,
            duration_seconds=5,
            enhance_prompt=True,
        ),
    )

    # Poll operation
    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    video = operation.result.generated_videos[0].video
    video.show()

Chats
=====

Create a chat session to start a multi-turn conversations with the model.

Send Message
------------

.. code:: python

    chat = client.chats.create(model='gemini-2.0-flash-001')
    response = chat.send_message('tell me a story')
    print(response.text)

Streaming
---------

.. code:: python

    chat = client.chats.create(model='gemini-2.0-flash-001')
    for chunk in chat.send_message_stream('tell me a story'):
        print(chunk.text, end='')

Async
-----

.. code:: python

    chat = client.aio.chats.create(model='gemini-2.0-flash-001')
    response = await chat.send_message('tell me a story')
    print(response.text)

Async Streaming
----------------

.. code:: python

    chat = client.aio.chats.create(model='gemini-2.0-flash-001')
    async for chunk in await chat.send_message_stream('tell me a story'):
        print(chunk.text, end='')

Files
======================

Files are only supported in Gemini Developer API.

.. code:: console

    gsutil cp gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf .
    gsutil cp gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf .

Upload
------

.. code:: python

    file1 = client.files.upload(file='2312.11805v3.pdf')
    file2 = client.files.upload(file='2403.05530.pdf')

    print(file1)
    print(file2)

Get
---

.. code:: python

    file1 = client.files.upload(file='2312.11805v3.pdf')
    file_info = client.files.get(name=file1.name)


Delete
------

.. code:: python

    file3 = client.files.upload(file='2312.11805v3.pdf')

    client.files.delete(name=file3.name)

Caches
======

``client.caches`` contains the control plane APIs for cached content

Create
------

.. code:: python

    if client.vertexai:
        file_uris = [
            'gs://cloud-samples-data/generative-ai/pdf/2312.11805v3.pdf',
            'gs://cloud-samples-data/generative-ai/pdf/2403.05530.pdf',
        ]
    else:
        file_uris = [file1.uri, file2.uri]

    cached_content = client.caches.create(
        model='gemini-2.0-flash-001',
        config=types.CreateCachedContentConfig(
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_uris[0], mime_type='application/pdf'
                        ),
                        types.Part.from_uri(
                            file_uri=file_uris[1],
                            mime_type='application/pdf',
                        ),
                    ],
                )
            ],
            system_instruction='What is the sum of the two pdfs?',
            display_name='test cache',
            ttl='3600s',
        ),
    )

Get
---

.. code:: python

    cached_content = client.caches.get(name=cached_content.name)

Generate Content
----------------

.. code:: python

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Summarize the pdfs',
        config=types.GenerateContentConfig(
            cached_content=cached_content.name,
        ),
    )
    print(response.text)

Tunings
=======

``client.tunings`` contains tuning job APIs and supports supervised fine
tuning through ``tune``.

Tune
----

-   Vertex AI supports tuning from GCS source
-   Gemini Developer API supports tuning from inline examples

.. code:: python

    if client.vertexai:
        model = 'gemini-2.0-flash-001'
        training_dataset = types.TuningDataset(
            gcs_uri='gs://cloud-samples-data/ai-platform/generative_ai/gemini-1_5/text/sft_train_data.jsonl',
        )
    else:
        model = 'models/gemini-2.0-flash-001'
        training_dataset = types.TuningDataset(
            examples=[
                types.TuningExample(
                    text_input=f'Input text {i}',
                    output=f'Output text {i}',
                )
                for i in range(5)
            ],
        )

.. code:: python

    tuning_job = client.tunings.tune(
        base_model=model,
        training_dataset=training_dataset,
        config=types.CreateTuningJobConfig(
            epoch_count=1, tuned_model_display_name='test_dataset_examples model'
        ),
    )
    print(tuning_job)

Get Tuning Job
--------------

.. code:: python

    tuning_job = client.tunings.get(name=tuning_job.name)
    print(tuning_job)

.. code:: python

    import time

    running_states = set(
        [
            'JOB_STATE_PENDING',
            'JOB_STATE_RUNNING',
        ]
    )

    while tuning_job.state in running_states:
        print(tuning_job.state)
        tuning_job = client.tunings.get(name=tuning_job.name)
        time.sleep(10)

Use Tuned Model
~~~~~~~~~~~~~~~

.. code:: python

    response = client.models.generate_content(
        model=tuning_job.tuned_model.endpoint,
        contents='why is the sky blue?',
    )

    print(response.text)

Get Tuned Model
---------------

.. code:: python

    tuned_model = client.models.get(model=tuning_job.tuned_model.model)
    print(tuned_model)

List Tuned Models
-----------------

To retrieve base models, see: :ref:`List Base Models`

.. code:: python

    for model in client.models.list(config={'page_size': 10, 'query_base': False}}):
        print(model)

.. code:: python

    pager = client.models.list(config={'page_size': 10, 'query_base': False}})
    print(pager.page_size)
    print(pager[0])
    pager.next_page()
    print(pager[0])

Async
~~~~~

.. code:: python

    async for job in await client.aio.models.list(config={'page_size': 10, 'query_base': False}}):
        print(job)

.. code:: python

    async_pager = await client.aio.models.list(config={'page_size': 10, 'query_base': False}})
    print(async_pager.page_size)
    print(async_pager[0])
    await async_pager.next_page()
    print(async_pager[0])

Update Tuned Model
------------------

.. code:: python

    model = pager[0]

    model = client.models.update(
        model=model.name,
        config=types.UpdateModelConfig(
            display_name='my tuned model', description='my tuned model description'
        ),
    )

    print(model)


List Tuning Jobs
----------------

.. code:: python

    for job in client.tunings.list(config={'page_size': 10}):
        print(job)

.. code:: python

    pager = client.tunings.list(config={'page_size': 10})
    print(pager.page_size)
    print(pager[0])
    pager.next_page()
    print(pager[0])

Async
~~~~~

.. code:: python

    async for job in await client.aio.tunings.list(config={'page_size': 10}):
        print(job)

.. code:: python

    async_pager = await client.aio.tunings.list(config={'page_size': 10})
    print(async_pager.page_size)
    print(async_pager[0])
    await async_pager.next_page()
    print(async_pager[0])

Batch Prediction
================

Only supported in Vertex AI.

Create
------

.. code:: python

    # Specify model and source file only, destination and job display name will be auto-populated
    job = client.batches.create(
        model='gemini-2.0-flash-001',
        src='bq://my-project.my-dataset.my-table',
    )

    job

.. code:: python

    # Get a job by name
    job = client.batches.get(name=job.name)

    job.state

.. code:: python

    completed_states = set(
        [
            'JOB_STATE_SUCCEEDED',
            'JOB_STATE_FAILED',
            'JOB_STATE_CANCELLED',
            'JOB_STATE_PAUSED',
        ]
    )

    while job.state not in completed_states:
        print(job.state)
        job = client.batches.get(name=job.name)
        time.sleep(30)

    job

List
----

.. code:: python

    for job in client.batches.list(config=types.ListBatchJobsConfig(page_size=10)):
        print(job)

.. code:: python

    pager = client.batches.list(config=types.ListBatchJobsConfig(page_size=10))
    print(pager.page_size)
    print(pager[0])
    pager.next_page()
    print(pager[0])

Async
~~~~~

.. code:: python

    async for job in await client.aio.batches.list(
        config=types.ListBatchJobsConfig(page_size=10)
    ):
        print(job)

.. code:: python

    async_pager = await client.aio.batches.list(
        config=types.ListBatchJobsConfig(page_size=10)
    )
    print(async_pager.page_size)
    print(async_pager[0])
    await async_pager.next_page()
    print(async_pager[0])

Delete
------

.. code:: python

    # Delete the job resource
    delete_job = client.batches.delete(name=job.name)

    delete_job

Error Handling
==============

To handle errors raised by the model, the SDK provides this [APIError](https://github.com/googleapis/python-genai/blob/main/google/genai/errors.py) class.

.. code:: python

    try:
        client.models.generate_content(
            model="invalid-model-name",
            contents="What is your name?",
        )
    except errors.APIError as e:
        print(e.code) # 404
        print(e.message)

Reference
=========
.. toctree::
   :maxdepth: 4

   genai