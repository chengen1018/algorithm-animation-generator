# Algorithm Animation Generator

An AI-powered tool that automatically generates beautiful Manim animations for algorithm visualization. Simply describe your algorithm and input data, and the system will create a fully-rendered educational video.

## ✨ Features

- 🤖 **AI-Powered Code Generation**: Leverages Google Gemini to automatically generate Manim animation code
- 🎨 **Visual Metaphor Designer**: Creates coherent visual design specifications for consistent and engaging animations
- 🎬 **Dual Template Modes**:
  - **Full Mode**: Complete educational layout with pseudocode, animation, and step-by-step explanations
  - **Simple Mode**: Pure animation focused on visual clarity
- 🔄 **Auto-Repair System**: Automatically detects and fixes rendering errors with up to 3 retry attempts
- 📊 **Multi-Algorithm Support**: Works with sorting, searching, graph algorithms, and more
- 📝 **Error Logging**: Comprehensive error snapshots for debugging and analysis

## 🚀 Getting Started

### Prerequisites

- [Manim Community Edition](https://www.manim.community/)
- Google API Key (for Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chengen1018/algorithm-animation-generator.git
   cd algorithm-animation-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   To get your API key:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into your `.env` file

### Usage

1. **Run the main script**
   ```bash
   python main.py
   ```

2. **Choose your template mode**
   ```
   Please select template mode:
   1. Full mode (pseudocode + animation + explanation)
   2. Pure animation mode (animation only)
   Select (1/2): 
   ```

3. **Provide algorithm details**
   ```
   Enter algorithm name (e.g., Bubble Sort): Bubble Sort
   Enter input data (e.g., [8, 2, 6, 4]): [64, 34, 25, 12, 22, 11, 90]
   ```

4. **Wait for generation**
   
   The system will:
   - Generate visual design specifications
   - Create Manim animation code
   - Render the animation
   - Automatically open the video upon completion

## 📂 Project Structure

```
algorithm-animation-generator/
├── main.py                          # Main entry point
├── llm_client.py                    # Google Gemini API client
├── visual_metaphor_designer.py     # Visual design specification generator
├── base_algorithm_scene.py          # Full mode base class
├── simple_animation_scene.py        # Simple mode base class
├── prompt_template.txt              # Full mode prompt template
├── prompt_template_simple.txt       # Simple mode prompt template
├── visual_metaphor_prompt.txt       # Visual design prompt template
├── requirements.txt                 # Python dependencies
├── .env                             # API keys (create this)
├── generated_algo_scene.py          # Auto-generated animation code
├── media/                           # Rendered videos and images
├── result/                          # Final output videos
└── error_logs/                      # Error snapshots and logs
```

## 🎯 How It Works

### 1. Visual Metaphor Generation
The system first analyzes your algorithm and generates a comprehensive visual design specification including:
- Shape choices for different elements (e.g., rounded rectangles for array elements)
- Color scheme for different states (comparing, swapping, sorted)
- Camera movement suggestions
- Layout strategy
- Animation style and pacing

### 2. Code Generation
Using the visual specifications and algorithm details, the AI generates production-ready Manim code that:
- Inherits from the appropriate base class
- Implements the algorithm logic
- Creates visually coherent animations
- Follows best practices for Manim animations

### 3. Auto-Repair Loop
If the initial code fails to render:
1. Error message is captured
2. Code and error log are saved to `error_logs/`
3. AI analyzes the error and generates a fix
4. Process repeats up to 3 times
5. Successfully rendered video opens automatically

## 📋 Supported Input Formats

### Arrays and Lists
```python
[64, 34, 25, 12, 22, 11, 90]
```

### Graphs
```python
# Adjacency list
{
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

# Edge list with weights
[('A', 'B', 4), ('B', 'C', 2), ('A', 'C', 5)]
```

### Trees
```python
# Level-order representation
[1, 2, 3, 4, 5, None, 7]
```

## 🎨 Template Modes

### Full Mode (Template 1)
Creates a three-panel layout:
- **Left Panel**: Pseudocode with current line highlighting
- **Center Panel**: Main animation area
- **Right Panel**: Explanation text and variable tracking

Perfect for educational content and detailed walkthroughs.

### Simple Mode (Template 2)
Pure animation with full-screen visualization:
- Maximum space for animation
- Focus on visual clarity
- Ideal for presentations and demonstrations

## 🔧 Configuration

### Rendering Quality
By default, animations render at low quality (`-pql`) for faster preview. To render in higher quality:

```python
# In main.py, modify the _render_manim_core function:
result = subprocess.run(
    ["manim", "-pqh", GENERATED_CODE_PATH, MANIM_CLASS_NAME],  # -pqh for 1080p
    # or
    ["manim", "-pqk", GENERATED_CODE_PATH, MANIM_CLASS_NAME],  # -pqk for 4K
    ...
)
```

### Model Selection
Change the AI model in `llm_client.py`:

```python
def generate_manim_code(prompt: str, model_name: str = "gemini-3-pro-preview"):
    # Available options: gemini-pro, gemini-3-pro-preview, etc.
```

## 📚 Examples

### Example 1: Bubble Sort
```bash
Algorithm: Bubble Sort
Input: [64, 34, 25, 12, 22, 11, 90]
```

### Example 2: Binary Search
```bash
Algorithm: Binary Search
Input: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
```

### Example 3: Dijkstra's Algorithm
```bash
Algorithm: Dijkstra's Shortest Path
Input: {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 5)], 3: []}
```

## 🐛 Troubleshooting

### API Key Issues
- Ensure your `.env` file is in the project root directory
- Verify your API key is valid and has sufficient quota
- Check that `python-dotenv` is installed

### Rendering Errors
- Check the `error_logs/` directory for detailed error messages
- Ensure Manim is properly installed: `manim --version`
- Try running with a simpler algorithm first

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Manim Community Edition, not the old ManimGL

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is available for educational and research purposes.

## 🙏 Acknowledgments

- [Manim Community](https://www.manim.community/) - The animation engine
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI code generation
- All algorithm educators and visualization enthusiasts

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using Manim and AI**
