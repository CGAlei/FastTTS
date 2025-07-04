# Complete the learning loop


### **Current System Overview:**
You have a Chinese language learning app with karaoke-style text interaction where users click words to get definitions in a right sidebar. The system uses FastHTML + HTMX for responsive UI updates.

### **Existing Workflow:**
1. User clicks Chinese word → HTMX queries `vocab.db` database
2. **If word exists**: Display stored information in right sidebar
3. **If word NOT found**: Show Google Translate fallback + "DEFINE" button
4. **Current gap**: DEFINE button doesn't complete the workflow

### **Required Implementation:**

#### **DEFINE Button Functionality:**
```python
# When DEFINE button is clicked, implement this workflow:

@app.post("/define-word")
def define_word(word: str):
    # 1. LLM API Call (Priority: OpenRouter → OpenAI fallback)
    llm_response = call_llm_api(word)  # Returns structured JSON
    
    # 2. Parse JSON response into database fields
    word_data = parse_llm_response(llm_response)
    
    # 3. Store in vocab.db
    save_to_database(word_data)
    
    # 4. Return HTMX response to update ONLY the word container
    return Div(
        # Updated word info display
        hx_swap_oob="true",  # Out-of-band swap
        id=f"word-{word}-container"  # Target specific word container
    )
```

#### **Technical Requirements:**

**1. LLM Integration:**
- Primary: OpenRouter API call
- Fallback: OpenAI API if OpenRouter fails
- Prompt for structured JSON response with word details
- Handle API errors gracefully

**2. Database Operations:**
- Insert new word data into `vocab.db`
- Use existing table schema fields
- Handle duplicate entries (update vs insert)

**3. HTMX Update Strategy:**
- Use `hx-swap-oob="true"` for targeted updates
- Update only the specific word container that was clicked
- Maintain UI state (don't refresh entire sidebar)
- Preserve scroll position and other interactions

**4. User Experience Flow:**
```
User clicks word → Shows Google Translate + DEFINE button
User clicks DEFINE → API call happens (with loading indicator)
API completes → Word data saved to database
UI updates → Same word now shows full LLM-generated information
Result: Word container transforms from "temporary" to "permanent" state
```

#### **Key Implementation Points:**

**Async Processing**: Use HTMX indicators for loading states during LLM calls
**Error Handling**: Graceful fallbacks if LLM APIs fail
**Data Persistence**: Ensure vocab.db receives properly formatted data
**UI Consistency**: Updated word should look identical to database-retrieved words
**Performance**: Only update the specific word container, not the entire sidebar

### **End Goal:**
Complete the learning loop where users can both **consume** existing word data and **generate** new word data seamlessly, with all information persistently stored and instantly available for future sessions.

**This creates a self-improving vocabulary database that grows with user interactions while maintaining fast, responsive UI updates.**