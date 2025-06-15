# X Follower Analyzer

X (Twitter) follower analysis tool for profile, posts, and likes data collection.

## Features

- Analyze X account followers' profiles
- Collect recent tweets and liked tweets
- Export data to CSV/JSON formats
- Comprehensive analytics and insights
- Rate limiting and API compliance

## Installation

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the `config/` directory:

```
X_BEARER_TOKEN=your_bearer_token_here
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## Usage

```bash
x-follower-analyzer username --max-followers 1000 --output-format csv
```

## Development

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run linting
make lint

# Run all CI checks
make ci
```

## License

MIT License
