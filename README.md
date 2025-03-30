# MedAgentSim: Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![GitHub contributors](https://img.shields.io/github/contributors/MAXNORM8650/MedAgentSim)](https://github.com/MAXNORM8650/MedAgentSim/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/MAXNORM8650/MedAgentSim)](https://github.com/MAXNORM8650/MedAgentSim/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/MAXNORM8650/MedAgentSim)](https://github.com/MAXNORM8650/MedAgentSim/network/members)
[![GitHub issues](https://img.shields.io/github/issues/MAXNORM8650/MedAgentSim)](https://github.com/MAXNORM8650/MedAgentSim/issues)
[![License](https://img.shields.io/github/license/MAXNORM8650/MedAgentSim)](https://github.com/MAXNORM8650/MedAgentSim/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

<div align="center">
  <img src="assets/medasim_logo.png" alt="MedAgentSim Logo" width="300"/>
  <p><i>An open-source framework for simulating realistic doctor-patient interactions</i></p>
</div>

## 🔍 Overview

MedAgentSim is an open-source simulated hospital environment designed to evaluate and enhance large language model (LLM) performance in dynamic diagnostic settings. Unlike prior approaches, our framework requires doctor agents to actively engage with patients through multi-turn conversations, requesting relevant medical examinations and imaging results to mimic real-world diagnostic processes.

Key features:
- **Multi-Agent Architecture**: Doctor, patient, and measurement agents interact in a realistic clinical setting
- **Self-Improvement Mechanisms**: Models iteratively refine their diagnostic strategies through experience
- **Experience Replay**: Past successful diagnoses inform future cases through knowledge retrieval
- **Visual Game Simulation**: Built with Phaser for an intuitive, interactive environment
- **Multi-Modal Capabilities**: Integration with vision language models for medical image interpretation

## 🚀 Quick Start

### Prerequisites

```bash
# Clone the repository
git clone https://github.com/MAXNORM8650/MedAgentSim.git
cd MedAgentSim

# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulation

```bash
# Start the server
python -m medsim.server

# In a separate terminal, launch the client
python -m medsim.client
```

Visit `http://localhost:8000` in your browser to interact with the simulation.

## 🏥 Simulation Modes

MedAgentSim supports three core interaction modes:

1. **Generation Mode**: Patient agent autonomously creates cases, generating illnesses, symptoms, and test results
2. **Dataset Mode**: Patient responses derived from predefined medical datasets
3. **Control Mode**: Human users can control either the doctor or patient agent for real-time interaction

## 🧠 Model Support

MedAgentSim is compatible with various LLMs:

- **Open-Source Models**: LLaMA 3.3, Mistral, Mixtral, Qwen2
- **Vision-Language Models**: LLaVA 1.5, QwenVL
- **Custom Models**: Integrate your own models following our documentation

## 📊 Benchmarks

MedAgentSim has been evaluated on several medical benchmarks:

| Benchmark | Description | #Cases |
|-----------|-------------|--------|
| NEJM | Complex real-world cases | 15 |
| NEJM Extended | Additional complex cases | 120 |
| MedQA | Simulated diagnostic scenarios | 106 |
| MedQA Extended | Extended diagnostic scenarios | 214 |
| MIMIC-IV | Real-world clinical cases | 288 |

## 📚 Citation

If you use MedAgentSim in your research, please cite our paper:

```bibtex
@article{almansoori2025selfevolving,
  title={Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions},
  author={Almansoori, Mohammad and Kumar, Komal and Cholakkal, Hisham},
  journal={arXiv preprint},
  year={2025}
}
```

## 🧩 Project Structure

```
MedAgentSim/
├── assets/               # Images, CSS, and other static files
├── data/                 # Sample datasets and medical knowledge base
├── docs/                 # Documentation
├── medsim/               # Core simulation code
│   ├── agents/           # Agent implementations
│   ├── environment/      # Simulation environment
│   ├── models/           # Model interfaces
│   ├── utils/            # Utility functions
│   ├── server.py         # Server implementation
│   └── client.py         # Client implementation
├── examples/             # Example scenarios and configurations
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── LICENSE               # License information
└── README.md             # This file
```

## 🛠️ Development

### Adding a Custom Agent

```python
from medsim.agents import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, name, role, **kwargs):
        super().__init__(name, role, **kwargs)
        
    def process_observation(self, observation):
        # Process the observation
        pass
        
    def decide_action(self):
        # Decide the next action
        pass
```

### Implementing a New Model

```python
from medsim.models import BaseModel

class MyCustomModel(BaseModel):
    def __init__(self, model_path, **kwargs):
        super().__init__(model_path, **kwargs)
        
    def generate(self, prompt, **kwargs):
        # Generate a response
        pass
```

## 👥 Contributing

We welcome contributions to MedAgentSim! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Mohamed bin Zayed University of Artificial Intelligence for supporting this research
- Contributors to the open-source LLM community
- Medical professionals who provided domain expertise and validation

## 📞 Contact

For questions or support, please open an issue or contact the maintainers:

- GitHub: [@MAXNORM8650](https://github.com/MAXNORM8650)
- Email: medsim@example.com

---

<div align="center">
  <p>Made with ❤️ by the MedAgentSim Team</p>
</div>