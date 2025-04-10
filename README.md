# Xerck CLI

A command-line tool for quickly setting up and managing React/Next.js projects with pre-built components.

## Installation

```bash
npm install -g xerck-cli
```

## Requirements

- Node.js project with a valid package.json file
- NPM or Yarn package manager

## Usage

```bash
xerck-cli <command> [options]
```

### Available Commands

- `init`: Initialize a Xerck project structure in your existing Node.js project

  - Creates components and lib directories
  - Sets up a globals.css file in the app directory
  - Installs necessary dependencies (clsx, tailwind-merge)
- `add <name>`: Add a pre-built component to your project

  - Downloads component from the Xerck component library
  - Automatically creates the component file in your components directory
- `version`: Display the current version of Xerck CLI

## Examples

### Initialize a project

```bash
# Navigate to your Node.js project directory
cd your-project

# Initialize Xerck
xerck-cli init
```

### Add a component

```bash
# Add a button component
xerck-cli add button

# Add a card component
xerck-cli add card
```

## Project Structure

After initialization, your project will have the following structure:

```
your-project/
├── components/     # Your UI components
├── lib/
│   └── utils.ts    # Utility functions
└── app/
    └── globals.css # Global styles
```

## Version

Current version: 1.0.4
