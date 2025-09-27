# Judge0 API Setup

## Configuration

To use Judge0 API for code execution, you need to set up the following environment variables:

### 1. Get Judge0 API Key
1. Go to [RapidAPI Judge0](https://rapidapi.com/judge0-official/api/judge0-ce/)
2. Subscribe to the API (free tier available)
3. Get your API key

### 2. Environment Variables
Add these to your `.env` file:

```env
# Judge0 API Configuration
JUDGE0_API_HOST=judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your-judge0-api-key-here
```

### 3. Features
- **Supported Languages**: Python, JavaScript, Java, C++
- **Batch Execution**: Run multiple test cases simultaneously
- **Error Handling**: Comprehensive error messages and debugging
- **Fallback**: Automatically falls back to local execution if Judge0 fails

### 4. Usage
In the frontend, you can toggle "Judge0 API" checkbox to use remote execution instead of local execution.

## Benefits of Judge0
- **Isolated Execution**: Code runs in secure sandboxed environments
- **Better Performance**: Optimized for competitive programming
- **Comprehensive Testing**: Supports complex test cases and edge cases
- **Language Support**: Wide range of programming languages
- **Scalability**: Handles high-volume code execution requests

## Fallback Strategy
If Judge0 API is unavailable or fails:
1. System automatically falls back to local execution
2. User experience remains uninterrupted
3. All features continue to work normally
