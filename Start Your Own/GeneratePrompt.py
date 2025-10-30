"""Wrapper for generate_prompt.py using local data directory."""

from pathlib import Path
import sys

# Add parent directory and current directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parent))

# Import from the current directory
import generate_prompt
generate_chatgpt_prompt = generate_prompt.generate_chatgpt_prompt

if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent
    
    # Prompt for starting equity for S&P comparison
    try:
        starting_equity_str = input("Enter your starting equity (for S&P 500 comparison), or press Enter to skip: ").strip()
        starting_equity = float(starting_equity_str) if starting_equity_str else None
    except ValueError:
        print("Invalid input. Skipping S&P 500 comparison.")
        starting_equity = None
    
    # Generate the prompt
    output_file = data_dir / "prompt.md"
    prompt = generate_chatgpt_prompt(data_dir, output_file, starting_equity)
    
    print("\n" + "="*60)
    print("Generated prompt saved to:", output_file)
    print("="*60)
    print("\nYou can now copy the contents of prompt.md and paste it into ChatGPT!")
