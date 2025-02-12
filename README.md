<div align="center">
  <h1>Building your Second Brain AI assistant using LLMs and RAG</h1>
  <h3>Learn how to access the collective wisdom of your own mind</h3>
  <p class="tagline">Open-source course by <a href="https://decodingml.substack.com">Decoding ML</a> in collaboration with </br> <a href="https://rebrand.ly/second-brain-course-mongodb">MongoDB</a>, <a href="https://rebrand.ly/second-brain-course-comet">Comet</a>, <a href="https://rebrand.ly/second-brain-course-opik">Opik</a>, <a href="https://rebrand.ly/second-brain-course-unsloth">Unsloth</a> and <a href="https://rebrand.ly/second-brain-course-zenml">ZenML</a>.</p>
</div>

</br>

<p align="center">
  <a href="https://decodingml.substack.com/p/build-your-second-brain-ai-assistant">
    <img src="static/system_architecture.png" alt="Architecture" width="600">
  </a>
</p>

## 📖 About This Course

This course is part of Decoding ML's open-source series, where we provide free hands-on resources for building GenAI systems using LLMs, RAG, agents and LLMOps.

Following Decoding ML's mission, in this course we will show you how to build an end-to-end AI system while building a Second Brain AI Assistant to chat with your Second Brain (aka your personal knowledge base, such as personal notes, resources, storage, etc.).

**The Second Brain AI Assistant** open-source course contains 6 modules and it's backed up by code and lessons that will teach you how to build an **advanced RAG and LLM system using LLMOps and ML systems best practices**.

By the end of this course, you will know how to architect and implement a production-ready agenticRAG and LLM system, by building an end-to-end GenAI application from scratch.

#### So What Is the Second Brain AI Assistant?

The concept of a Second Brain is a metaphor coined by Tiago Forte to describe the process of building a personal knowledge base, where you store your notes, ideas, and resources.

The Second Brain AI Assistant is an AI assistant that uses your Second Brain as a source of knowledge to answer questions, summarize documents, and provide insights.

For example, based on your research, instead of searching and readingyour notes,you could ask your Second Brain AI Assistant to recommend you a course on agents, to list the top 5 tools on parsing PDF documents or to summarize what are the main methods to optimize LLMs during inference.

As this is an educative open-source project, we will stick to Notion as our source of knowledge, but the code can be easily adapted to other sources, such as Google Drive, Calendar, etc.

As a fun (and relevant) example, we will provide you with our list of filtered resources (which we keep in Notion) on AI and ML, such as GenAI, LLMs, RAG, MLOps, LLMOps and information retrieval. **Thus, you don't have to use Notion to take this course.** But if you want to, you can, as we expose in this GitHub repository, a flexible pipeline that can load any Notion database. 

### What You'll Do:

- Build an agentic RAG application that uses your Second Brain as a source of knowledge.
- Architect an agentic LLM and RAG system.
- Apply LLMOps and software engineering best practices.
- Fine-tune and deploy open-source LLMs.
- Leverage popular tools such as OpenAI, Hugging Face, MongoDB, ZenML, Opik, Comet, Unsloth, Crawl4AI, uv, ruff, smolagents, etc.

## 🎯 What You'll Learn

While building the Second Brain AI assistant, we will cover the following concepts, algorithms and tools:

- Architect an LLM system using the feature/training/inference (FTI) architecture.
- Use MLOps best practices such as data registries, model registries, and experiment trackers.
- Crawl over 700 links and normalize everything into Markdown using Crawl4AI.
- Compute quality scores using LLMs.
- Generate summarization datasets using distillation.
- Fine-tune a Llama model using Unsloth and Comet.
- Deploy a Llama model as an inference endpoint to Hugging Face serverless Dedicated Endpoints.
- Implement advanced RAG algorithms using contextual retrieval, hybrid search and MongoDB vector search.
- Build an agent that uses multiple tools using Hugging Face's smolagents framework.
- Use LLMOps best practices such as prompt monitoring and RAG evaluation using Opik.
- Integrate pipeline orchestration, artifact and metadata tracking using ZenML.
- Manage the Python project using uv and ruff. 

🥷 With these skills, you'll become a ninja in building **advanced agentic RAG and LLM systems using LLMOps and ML systems best practices**. 

## 👥 Who Should Join?

**This course is ideal for:**
- ML/AI engineers interested in building production-ready agentic RAG and LLM systems
- Data Engineers, Data Scientists, and Software Engineers wanting to level-up their engineering and system design skills to build production-ready AI systems

**Alert:** This course focuses on engineering practices and end-to-end system implementation rather than pure theory.

## 🎓 Prerequisites

| Category | Requirements |
|----------|-------------|
| **Skills** | - Intermediate understanding of Python <br/> - Begginer understanding of Machine Learning <br/> - Begginer understanding of LLMs <br/> - Begginer understanding of RAG |
| **Hardware** | Any modern laptop/workstation will do the job (no GPU or powerful computing power required). We will show you how to use the cloud for lessons that require a GPU. |
| **Level** | Intermediate (But with a little sweat and patience, anyone can do it) |


## 💰 Cost Structure

The course is open-source and free of charge. 

But you will need to pay up between $1 - $5 for the tools we use throughout the course. **In case you just read the lessons and don't run the code, the costs are $0.**

All tools used throughout the course will stick to their free tier, except a few pay-as-you-go tools.

| Service | Maximum Cost |
|---------|--------------|
| OpenAI's API | ~$3 |
| Hugging Face's Dedicated Endpoints (Optional) | ~$2 |

The amazing thing about our course is that we provide multiple paths to take our course, to avoid running certain modules or algorithms that cost more, such as the deployment of the LLM. 

Thus, in the minimal **path** of the course, **you can run the entire course with ~$1 costs**, mainly due to module 6, where you test the Second Brain AI assistant.

## 🥂 Open-source Course: Participation is Open and Free

As an open-source course, you don't have to enroll. Everything is self-paced, free of charge and with its resources freely accessible as follows:
- **code**: this GitHub repository
- **lessons**: [Decoding ML](https://decodingml.substack.com/p/build-your-second-brain-ai-assistant)

## 📚 Course Outline

This **open-source course consists of 6 comprehensive modules** covering theory, system design, and hands-on implementation.

Our recommendation for getting the most out of this course:
1. Clone the repository.
2. Read the materials.
3. Setup the code and run it to replicate our results.
4. Go deeper into the code to understand the details of the implementation.

| Module | Materials | Description | Running the code |
|--------|-----------|-------------|------------------|
| 1 | [Build your Second Brain AI assistant](https://decodingml.substack.com/p/build-your-second-brain-ai-assistant) | Architect an AI assistant for your Second Brain. | **No code** |
| 2 | Data pipelines for building AI assistants (WIP) | Build a data pipeline to process Notion data, crawl new documents, compute a quality score using LLMs and ingest them to a NoSQL database. | [apps/second-brain-offline](apps/second-brain-offline) |
| 3 | Generate high-quality fine-tuning datasets (WIP) | Generate a high-quality summarization instruct dataset using distilation. | [apps/second-brain-offline](apps/second-brain-offline) |
| 4 | Fine-tune and deploy open-source LLMs (WIP) | Fine-tune an open-source LLM to specialize it in summarizing documents and deploy it as a real-time endpoint. | [apps/second-brain-offline](apps/second-brain-offline) |
| 5 | RAG feature pipelines for building AI assistants (WIP) | Implement an RAG feature pipeline using advanced techniques such as context retrieval. | [apps/second-brain-offline](apps/second-brain-offline) |
| 6 | Agents and LLMOps (WIP) | Implement the agentic inference pipeline together with an observation pipeline to monitor and evaluate the performance of the AI assistant. | [apps/second-brain-online](apps/second-brain-online) |

## 🏗️ Project Structure

While building the Second Brain AI assistant, we will build two separate Python applications:

```bash
.
├── apps / 
|   ├── infrastructure/               # Docker infrastructure for the applications
|   |   ├── second-brain-offline/     # Offline ML pipelines
└─  └─  └── second-brain-online/      # Online inference pipeline = our AI assistant
```

## 👔 Dataset

We will use our personal list of filtered resources (which we keep in Notion) on AI and ML, such as GenAI, LLMs, RAG, MLOps, LLMOps and information retrieval, containing ~100 pages and 500+ links which we will crawl and access from the Second Brain AI assistant.

![Notion data](./static/notion_genai_dataset.png)

For ease of use, we stored a snapshot of our Notion data in a public S3 bucket, which you can download for free without AWS credentials.

[Download here](https://decodingml-public-data.s3.eu-central-1.amazonaws.com/second_brain_course/notion/notion.zip)

Thus, you don't need to use Notion or hook your Notion to complete this course. But if you want to, you can, as we expose in this GitHub repository, a flexible pipeline that can load any Notion database. 

## 🚀 Getting Started

For detailed installation and usage instructions, see each application documentation that will walk you through how to setup everything and run the code for each module:

| Application | Documentation |
|------------|---------------|
| Offline ML Pipelines | [apps/second-brain-offline](apps/second-brain-offline) |
| Online Inference Pipeline </br> (the Second Brain AI assistant) | [apps/second-brain-online](apps/second-brain-online) |

**Recommendation:** While you can follow the installation guide directly, we strongly recommend reading the accompanying articles to gain a complete understanding of what you'll build.

## 💡 Questions and Troubleshooting

Have questions or running into issues? We're here to help!

Open a [GitHub issue](https://github.com/decodingml/second-brain-ai-assistant-course/issues) for:
- Questions about the course material
- Technical troubleshooting
- Clarification on concepts

## 🥂 Contributing

As an open-source course, we may not be able to fix all the bugs that arise.

If you find any bugs and know how to fix them, support future readers by contributing to this course with your bug fix.

You can always contribute by:
- Forking the repository
- Fixing the bug
- Creating a pull request

We will deeply appreciate your support for the AI community and future readers 🤗

## Sponsors

<div align="center">
  <table style="border-collapse: collapse; border: none;">
    <tr style="border: none;">
      <td align="center" style="border: none; padding: 20px;">
        <a href="https://rebrand.ly/second-brain-course-mongodb" target="_blank">
          <img src="static/sponsors/mongo.png" width="200" style="max-height: 45px; width: auto;" alt="MongoDB">
        </a>
      </td>
      <td align="center" style="border: none; padding: 20px;">
        <a href="https://rebrand.ly/second-brain-course-comet" target="_blank">
          <img src="static/sponsors/comet.png" width="200" style="max-height: 45px; width: auto;" alt="Comet">
        </a>
      </td>
      <td align="center" style="border: none; padding: 20px;">
        <a href="https://rebrand.ly/second-brain-course-opik" target="_blank">
          <img src="static/sponsors/opik.png" width="200" style="max-height: 45px; width: auto;" alt="Opik">
        </a>
      </td>
      <td align="center" style="border: none; padding: 20px;">
        <a href="https://rebrand.ly/second-brain-course-unsloth" target="_blank">
          <img src="static/sponsors/unsloth.png" width="200" style="max-height: 45px; width: auto;" alt="Unsloth">
        </a>
      </td>
      <td align="center" style="border: none; padding: 20px;">
        <a href="https://rebrand.ly/second-brain-course-zenml" target="_blank">
          <img src="static/sponsors/zenml.png" width="200" style="max-height: 45px; width: auto;" alt="ZenML">
        </a>
      </td>
    </tr>
  </table>
</div>

## Core Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/iusztinpaul">
        <img src="https://github.com/iusztinpaul.png" width="100px;" alt="Paul Iusztin"/><br />
        <sub><b>Paul Iusztin</b></sub>
      </a><br />
      <sub>AI/ML Engineer</sub>
    </td>
     </td>
     <td align="center">
      <a href="https://github.com/ernestol0817">
        <img src="https://github.com/ernestol0817.png" width="100px;" alt="Ernesto Larios"/><br />
        <sub><b>Ernesto Larios</b></sub>
      </a><br />
      <sub>AI Engineer</sub>
    </td>
    <td align="center">
      <a href="https://github.com/915-Muscalagiu-AncaIoana">
        <img src="https://github.com/915-Muscalagiu-AncaIoana.png" width="100px;" alt="Anca Ioana Muscalagiu"/><br />
        <sub><b>Anca Ioana Muscalagiu</b></sub>
      </a><br />
      <sub>SWE/ML Engineer</sub>
  </tr>
</table>


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
