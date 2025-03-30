from setuptools import setup, find_packages

setup(
    name="magent",
    version="0.1.0",
    author="MedAgentSim",
    description="MedAgentSim: Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions",
    url="https://github.com/MAXNORM8650/MedAgentSim",  # Replace with the URL of your project
    packages=find_packages(),
    install_requires=[
        "datasets",
        "tqdm",
        "openai",
        "python-liquid",
        "GitPython",
        "torch",
        "scikit-learn",
        "vLLM",
    ],
    python_requires=">=3.9",  # Specify the minimum Python version required
)