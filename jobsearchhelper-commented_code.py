# This is like importing tools from a toolbox - we need these special tools to work with our code
import os  # This tool helps us talk to our computer's operating system (like asking for passwords stored safely)
from langchain_openai import OpenAIEmbeddings  # This is a special tool that can understand and convert text into numbers that computers can work with
from langchain_community.document_loaders import TextLoader  # This tool helps us read text files, like opening a book
from langchain_text_splitters import RecursiveCharacterTextSplitter  # This tool cuts big text into smaller, manageable pieces (like cutting a pizza into slices)
from langchain_chroma import Chroma  # This is like a smart filing cabinet that can store and find documents quickly


# Think of this like asking your computer "Hey, do you remember my OpenAI password?"
# os.getenv looks for a secret password stored safely on your computer
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# This creates our "text understanding machine" using the password we just got
# It's like hiring a really smart assistant who can read and understand text
llm=OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# This opens and reads a file called "job_listings.txt" - like opening a book and reading all the pages
# The .load() part actually does the reading and puts all the text into our program's memory
document = TextLoader("job_listings.txt").load()

# This creates our "text cutter" tool with specific settings:
# chunk_size=200 means "cut the text into pieces of about 200 characters each" (like limiting each paragraph)
# chunk_overlap=10 means "when you cut, let each piece share 10 characters with the next piece" (so we don't lose important connections)
text_splitter= RecursiveCharacterTextSplitter(chunk_size=200,
                                              chunk_overlap=10)

# Now we actually use our text cutter to chop up our document into smaller pieces
# It's like taking a long story and breaking it into short paragraphs that are easier to work with
chunks=text_splitter.split_documents(document)

# This creates our smart filing cabinet and immediately fills it with our text chunks
# The filing cabinet (Chroma) uses our smart assistant (llm) to understand and organize each piece
# It's like having a librarian who reads each piece and knows exactly where to file it for quick finding later
db=Chroma.from_documents(chunks,llm)

# This creates a "search helper" from our filing cabinet
# Think of it as getting a search function that can find the most relevant pieces of text when you ask a question
retriever = db.as_retriever()

# This asks the user (you!) to type in a question or search term
# It's like asking "What would you like to search for in all these job listings?"
text = input("Enter the query")

# This takes your question and asks our search helper to find the most relevant pieces of text
# It's like telling your librarian "Find me all the documents that relate to this question"
docs = retriever.invoke(text)

# This goes through each document that was found and prints out its content
# It's like the librarian bringing you a stack of relevant papers and you reading each one out loud
for doc in docs:  # "for each document in the stack of documents we found..."
    print(doc.page_content)  # "...print out what's written on that document"