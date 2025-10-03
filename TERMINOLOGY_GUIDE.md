# Intel CPU Crawler - Terminology Guide

## Purpose
This document defines the key terms and vocabulary used in the Intel CPU Crawler project. It serves as a reference to ensure clear communication between team members and consistent terminology throughout the codebase.

**Note**: English is a complex language with technical jargon. This guide is here to help! Feel free to use these terms in prompts, and we'll expand this document as we encounter new concepts.

---

## Table of Contents
- [Project Components](#project-components)
- [Data & Database Terms](#data--database-terms)
- [Web Scraping Terms](#web-scraping-terms)
- [Intel CPU Specifications](#intel-cpu-specifications)
- [Operations & Actions](#operations--actions)
- [Common Phrases](#common-phrases)
- [Alternative Terms (What You Might Say → What We Call It)](#alternative-terms)

---

## Project Components

### **Crawler**
- **Definition**: The main program that visits Intel websites and extracts CPU information
- **Example**: "Run the crawler to get new CPU data"
- **Related**: scraper, spider, bot

### **Parser**
- **Definition**: The component that reads HTML content and extracts structured data (like CPU specifications)
- **Example**: "The parser extracts the processor name from the page"
- **Related**: extractor, analyzer

### **Database** (DB)
- **Definition**: The SQLite file that stores all CPU specifications permanently
- **File**: `intel_cpu_power_specs.db`
- **Example**: "Add the new CPUs to the database"
- **Alternative terms**: "data storage", "the db", "database file"

### **Database Manager**
- **Definition**: The code component that handles reading from and writing to the database
- **Class**: `PowerSpecDatabaseManager`
- **Example**: "The database manager saves the CPU specs"

### **Update Tool** / **Updater**
- **Definition**: The automated program that checks for new Intel products and adds them to the database
- **File**: `update_database.py`
- **Example**: "Run the update tool weekly to check for new CPUs"
- **Alternative terms**: "periodic updater", "auto-updater", "update checker"

---

## Data & Database Terms

### **CPU Record** / **CPU Entry**
- **Definition**: A single row in the database representing one Intel processor
- **Example**: "The database contains 927 CPU records"
- **Alternative terms**: "CPU data", "processor entry", "one CPU"

### **Specification** / **Spec**
- **Definition**: A single piece of information about a CPU (like "Base Frequency: 3.5 GHz")
- **Example**: "Extract all specifications from the webpage"
- **Alternative terms**: "CPU detail", "property", "attribute"

### **Field** / **Column**
- **Definition**: A type of data stored for each CPU (like `processor_name`, `tdp`, `gpu_name`)
- **Example**: "The GPU name field was empty"
- **Alternative terms**: "database column", "data field", "property name"

### **Duplicate**
- **Definition**: A CPU that already exists in the database (detected by URL)
- **Example**: "Skip duplicates when adding new CPUs"
- **Alternative terms**: "already exists", "repeated entry", "same CPU"

### **URL** (Uniform Resource Locator)
- **Definition**: The web address of a CPU specification page
- **Example**: `https://www.intel.com/content/www/us/en/products/sku/240961/...`
- **Alternative terms**: "web address", "link", "page address"

### **Backup**
- **Definition**: A copy of the database file saved for safety
- **Example**: "Create a backup before updating the database"
- **Alternative terms**: "database copy", "safety copy", "backup file"

### **Merge** / **Combine**
- **Definition**: Taking data from two databases and putting them into one
- **Example**: "Merge the Core Ultra database with the main database"
- **Alternative terms**: "combine databases", "join databases", "put together"

---

## Web Scraping Terms

### **Scrape** / **Crawl**
- **Definition**: The process of automatically visiting webpages and extracting data
- **Example**: "Scrape the Intel ARK website for CPU specs"
- **Alternative terms**: "extract data", "collect data", "download information"

### **HTML**
- **Definition**: The code language that webpages are written in
- **Example**: "Parse the HTML to find the processor name"
- **Alternative terms**: "webpage code", "page source"

### **Parse** / **Extract**
- **Definition**: Reading HTML code and pulling out specific information
- **Example**: "Parse the specification table to get TDP values"
- **Alternative terms**: "extract from", "get data from", "read from"

### **Intel ARK**
- **Definition**: Intel's official product specification database website
- **URL**: `https://www.intel.com/content/www/us/en/ark.html`
- **Example**: "Check Intel ARK for new processor releases"
- **Alternative terms**: "Intel website", "Intel specification site"

### **Processor Family** / **Product Family**
- **Definition**: A group of related CPUs (like "14th Gen Intel Core i7")
- **Example**: "Crawl all 52 processor families"
- **Alternative terms**: "CPU series", "product line", "processor group"

### **Family Page** / **Series Page**
- **Definition**: A webpage listing all CPUs in a specific family
- **Example**: `https://www.intel.com/...14th-generation-intel-core-i7-processors.html`
- **Alternative terms**: "product list page", "family listing"

### **Specification Page** / **Product Page** / **Detail Page**
- **Definition**: A webpage with detailed specifications for one specific CPU
- **Example**: `https://www.intel.com/...core-i7-14700k.../specifications.html`
- **Alternative terms**: "CPU page", "detail page", "spec page"

### **Rate Limiting** / **Delay**
- **Definition**: Waiting between requests to avoid overloading Intel's servers
- **Example**: "Use a 2.5 second delay between requests"
- **Alternative terms**: "waiting time", "pause between requests", "slow down"

---

## Intel CPU Specifications

### **Processor Name** / **CPU Name**
- **Definition**: The official Intel product name
- **Example**: "Intel® Core™ i7-14700K Processor"
- **Alternative terms**: "processor model", "CPU model", "product name"

### **Core** / **CPU Core**
- **Definition**: An independent processing unit inside a CPU
- **Example**: "This CPU has 8 performance cores and 8 efficiency cores"
- **Types**: 
  - **P-core** (Performance Core): Fast, powerful cores
  - **E-core** (Efficiency Core): Slower, power-saving cores
- **Alternative terms**: "processor core", "computing core"

### **Thread**
- **Definition**: A virtual core created by hyper-threading technology
- **Example**: "8 cores, 16 threads"
- **Alternative terms**: "logical processor"

### **Frequency** / **Clock Speed**
- **Definition**: How fast a core operates, measured in GHz (gigahertz)
- **Types**:
  - **Base Frequency**: Normal operating speed
  - **Max Turbo Frequency**: Highest speed under boost
- **Example**: "Base: 3.4 GHz, Max Turbo: 5.6 GHz"
- **Alternative terms**: "speed", "clock rate", "processing speed"

### **TDP** (Thermal Design Power)
- **Definition**: The amount of power (in watts) the CPU consumes and heat it generates
- **Example**: "This CPU has a TDP of 125W"
- **Alternative terms**: "power consumption", "processor power", "wattage"

### **Lithography** / **Process Node**
- **Definition**: The manufacturing technology size (like 10nm, 7nm, Intel 7)
- **Example**: "Built on Intel 7 process technology"
- **Alternative terms**: "manufacturing process", "node size", "process technology"

### **Cache**
- **Definition**: Fast memory inside the CPU for quick data access
- **Types**: L1, L2, L3 (Smart Cache)
- **Example**: "24 MB Intel® Smart Cache"
- **Alternative terms**: "CPU memory", "cache memory"

### **GPU** (Graphics Processing Unit)
- **Definition**: The integrated graphics processor in the CPU
- **Example**: "Intel® UHD Graphics 770"
- **Alternative terms**: "integrated graphics", "graphics chip", "iGPU"

### **Socket**
- **Definition**: The physical connector type for the motherboard
- **Example**: "LGA1700 socket"
- **Alternative terms**: "CPU socket", "motherboard connector"

---

## Operations & Actions

### **Run** / **Execute**
- **Definition**: Start a program or script
- **Example**: "Run the updater to check for new CPUs"
- **Alternative terms**: "start", "launch", "execute"

### **Crawl** / **Collect** / **Gather**
- **Definition**: The process of visiting webpages and extracting data
- **Example**: "Crawl all processor families"
- **Alternative terms**: "scrape", "collect data", "fetch data"

### **Parse** / **Extract** / **Read**
- **Definition**: Analyze HTML and pull out specific information
- **Example**: "Parse the GPU name from the specifications"
- **Alternative terms**: "extract", "get", "read", "pull out"

### **Save** / **Store** / **Add** / **Insert**
- **Definition**: Put data into the database
- **Example**: "Save the CPU specifications to the database"
- **Alternative terms**: "add to database", "store", "insert", "write to database"

### **Update**
- **Definition**: Add new data or modify existing data
- **Example**: "Update the database with new processors"
- **Alternative terms**: "refresh", "add new data", "sync"

### **Check** / **Verify** / **Test**
- **Definition**: Look at something to see if it's correct or working
- **Example**: "Check if there are new products"
- **Alternative terms**: "verify", "test", "look at", "inspect"

### **Dry Run**
- **Definition**: Test mode that shows what would happen without actually making changes
- **Example**: "Do a dry run to see what new CPUs would be added"
- **Alternative terms**: "test mode", "preview mode", "check only (no changes)"

### **Live Update** / **Real Update**
- **Definition**: Actually make changes to the database (opposite of dry run)
- **Example**: "Run a live update to add the new CPUs"
- **Alternative terms**: "real run", "actual update", "make changes"

### **Push** (Git)
- **Definition**: Upload local code changes to GitHub
- **Example**: "Push the code to GitHub"
- **Alternative terms**: "upload to GitHub", "sync to remote", "commit and push"

### **Commit** (Git)
- **Definition**: Save code changes with a description message
- **Example**: "Commit the new updater tool"
- **Alternative terms**: "save changes", "record changes"

### **Backup**
- **Definition**: Create a copy of the database for safety
- **Example**: "Backup the database before major updates"
- **Alternative terms**: "make a copy", "create backup", "save a copy"

### **Merge** / **Combine**
- **Definition**: Take data from multiple sources and put into one
- **Example**: "Merge the two databases into one"
- **Alternative terms**: "combine", "join", "put together"

### **Filter** / **Exclude** / **Skip**
- **Definition**: Choose what data to include or exclude
- **Example**: "Skip duplicate entries when adding CPUs"
- **Alternative terms**: "exclude", "leave out", "don't include"

---

## Common Phrases

### "The parser does not get/extract [something]"
- **Meaning**: The parser is not successfully reading a specific piece of data
- **Example**: "The parser does not get the GPU name"
- **What to say**: "The parser isn't extracting the GPU name" or "GPU name extraction isn't working"

### "Can we crawl/parse all [something]?"
- **Meaning**: Is our tool able to extract data from all items in a group?
- **Example**: "Can we parse all 44 Core Ultra products?"
- **What to say**: "Can the crawler handle all 44 Core Ultra products?"

### "Let's push it"
- **Meaning**: Upload the code changes to GitHub
- **What to say**: "Let's push the code" or "Upload to GitHub" or "Commit and push"

### "Check for new products"
- **Meaning**: See if Intel has released any new CPUs since last check
- **What to say**: "Check for new Intel processors" or "Look for updates"

### "Add to database" / "Save to database"
- **Meaning**: Store the CPU information in the database file
- **What to say**: "Insert into database" or "Store in database" or "Save to DB"

### "Create/make a backup"
- **Meaning**: Copy the database file before making changes
- **What to say**: "Backup the database" or "Make a safety copy"

### "Preventing duplications" / "Avoid duplicates"
- **Meaning**: Make sure the same CPU isn't added to the database twice
- **What to say**: "Prevent duplicates" or "Check for existing entries" or "Skip if already exists"

### "Run periodically" / "Run regularly"
- **Meaning**: Execute the program on a schedule (like weekly or daily)
- **What to say**: "Schedule regular runs" or "Run on a schedule" or "Automated periodic execution"

---

## Alternative Terms
*What you might say → What we typically call it*

### Database Operations
- "Put data in database" → **Insert** / **Save** / **Add to database**
- "Get data from database" → **Query** / **Fetch** / **Retrieve** / **Read from database**
- "Change data in database" → **Update** / **Modify**
- "Remove from database" → **Delete** / **Remove**
- "Database copy" → **Backup**
- "Put databases together" → **Merge** / **Combine**

### Crawling Operations
- "Visit webpage" → **Crawl** / **Scrape** / **Fetch**
- "Read webpage" → **Parse** / **Extract from**
- "Get information from page" → **Extract** / **Parse** / **Scrape**
- "Visit many pages" → **Mass crawl** / **Bulk scrape** / **Crawl multiple pages**

### Data Terms
- "CPU information" → **Specifications** / **Specs** / **CPU data**
- "One CPU" → **CPU record** / **Entry** / **Row**
- "List of CPUs" → **Dataset** / **Collection** / **Records**
- "Same CPU already in database" → **Duplicate** / **Already exists**
- "New CPU not in database" → **New product** / **New entry** / **Not yet added**

### Code Operations
- "Upload to GitHub" → **Push** / **Commit and push**
- "Save code changes" → **Commit**
- "Get latest code" → **Pull** / **Fetch**
- "Test without changing" → **Dry run** / **Test mode**
- "Actually do it" → **Live run** / **Execute** / **Real update**

### File Terms
- "Computer program file" → **Script** / **Program** / **Tool**
- "Text file" → **File** / **Document**
- "Settings file" → **Configuration** / **Config file**
- "Database file" → **Database** / **DB file**
- "Instruction file" → **Documentation** / **Guide** / **README**

### Time/Frequency Terms
- "Wait between requests" → **Delay** / **Rate limiting** / **Throttling**
- "Run automatically on schedule" → **Scheduled execution** / **Periodic update** / **Automated run**
- "Run one time" → **Manual run** / **One-time execution**
- "Run many times" → **Repeated execution** / **Multiple runs**

---

## Tips for Effective Communication

### ✅ Clear Ways to Ask Questions

**Instead of**: "Can you make it do the thing?"  
**Try**: "Can you make the parser extract the GPU name?"

**Instead of**: "The program doesn't work"  
**Try**: "The crawler fails when parsing 14th gen processors" or "I get an error when running update_database.py"

**Instead of**: "Add the new stuff"  
**Try**: "Add the new CPU specifications to the database" or "Insert the crawled data"

**Instead of**: "Fix the database thing"  
**Try**: "Fix the duplicate detection in the database" or "Update the database merge logic"

### ✅ Describing Problems

When something doesn't work, try to include:
1. **What you tried**: "I ran update_database.py"
2. **What you expected**: "I expected it to find new CPUs"
3. **What happened**: "It said 'No new products found'"
4. **Any error messages**: Include the actual error text

### ✅ Useful Phrases

- "Can we...?" = Request to implement a feature
- "How do I...?" = Request for instructions
- "What does... mean?" = Request for explanation
- "Fix the..." = Request to solve a problem
- "Add/Create..." = Request to build something new
- "Check if..." = Request to verify something
- "Show me..." = Request for information/results

---

## Examples in Context

### Example 1: Asking about Data Extraction
**You might say**: "The tool doesn't see the processor speed"  
**We understand**: "The parser isn't extracting the frequency/clock speed specification"  
**Clear version**: "The parser doesn't extract the base frequency" or "Max turbo frequency is not being parsed"

### Example 2: Database Operations
**You might say**: "Put the new CPUs in the storage"  
**We understand**: "Insert the new CPU records into the database"  
**Clear version**: "Add the new CPUs to the database" or "Save new CPU specs to the DB"

### Example 3: Running Operations
**You might say**: "Make the program visit Intel's website and get all the info"  
**We understand**: "Run the crawler to scrape CPU specifications from Intel ARK"  
**Clear version**: "Crawl Intel ARK to extract CPU specs" or "Run the scraper on Intel's product pages"

### Example 4: Checking for Updates
**You might say**: "See if Intel has new processors"  
**We understand**: "Check for new Intel products not in the database"  
**Clear version**: "Run the updater to check for new CPUs" or "Check Intel ARK for new products"

---

## When in Doubt...

**Don't worry about using perfect technical terms!** If you're not sure what something is called:

1. **Describe what you want**: "I want to check if there are new processors without changing the database"
   - → We understand: "You want to run a dry-run update"

2. **Use simple words**: "Get the data from the webpage and save it"
   - → We understand: "Scrape the page and save to database"

3. **Ask for clarification**: "What do you call the thing that stores CPU information?"
   - → We'll explain: "That's the database (intel_cpu_power_specs.db)"

4. **Point to examples**: "Do the same thing we did yesterday" or "Like the Core Ultra crawl"

---

## Expanding This Document

This is a living document! When you encounter:
- **New concepts** → We'll add them here
- **Confusing terms** → We'll clarify them
- **Better ways to explain** → We'll update the definitions

Just say: *"Can we add [term] to the terminology guide?"* or *"I don't understand what [term] means"*

---

## Quick Reference Card

| You Want To... | Say This | File/Command |
|---------------|----------|--------------|
| Check for new Intel CPUs (safe) | "Run a dry-run update" | `check_for_updates.bat` |
| Add new CPUs to database | "Run the updater" or "Update the database" | `run_update.bat` |
| Get all CPU data from scratch | "Run mass crawl" or "Crawl all families" | `crawl_all_families.py` |
| Copy database safely | "Create a backup" | Manual copy |
| Combine two databases | "Merge databases" | `merge_databases.py` |
| Upload code to GitHub | "Push the code" | `git push` |
| Test without changes | "Do a dry run" | `--dry-run` flag |

---

**Last Updated**: October 3, 2025  
**Project**: Intel CPU Crawler  
**Version**: 1.0

*Feel free to refer to this guide anytime, and let's keep expanding it together!*
