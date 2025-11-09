# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

AIL (Analysis Information Leak) is a modular framework for analyzing potential information leaks from unstructured data sources like pastes, forums, and the dark web. It automatically detects, extracts, and correlates sensitive information such as credentials, payment card numbers, API keys, and private keys.

### Key Technologies

- **Language**: Python 3.8+
- **Web Framework**: Flask 2.3.3+ (port 7000)
- **Databases**:
  - Redis (3 instances on ports 6379-6381) for caching and queuing
  - Kvrocks (port 6383) for persistent key-value storage
  - Meilisearch for full-text search
- **Message Queue**: ZMQ for inter-module communication
- **Async Processing**: Python modules run as independent processes managed by screen
- **Key Libraries**: pyail, pylacus, pymisp, yara-python, scrapy, nltk, beautifulsoup4

## Project Structure

```
bin/
  core/              # Core infrastructure (sync, importers, D4 client, crawler manager)
  modules/           # 30+ analysis modules (extraction, pattern detection, deduplication, correlation)
  crawlers/          # Web/Tor hidden service crawler (Lacus wrapper)
  importer/          # Data importers (ZMQ, Feeder, Crawler, MISP, Pystemon, File uploads)
  exporter/          # Data exporters (MISP, TheHive, Mail, Webhooks)
  trackers/          # User-defined pattern tracking (YARA, regex, term, typo squatting)
  lib/
    objects/         # AIL object models (Items, Domains, Credentials, Decodeds, etc.)
    ail_queue.py     # ZMQ-based message queue system
    ConfigLoader.py  # Configuration management
    ail_logger.py    # Logging utilities
  packages/          # Bundled external packages

var/www/
  blueprints/        # Flask route handlers (~36 endpoints)
  templates/         # HTML/Jinja2 templates
  static/            # JavaScript, CSS, assets
  Flask_server.py    # Flask application entry point

configs/             # Configuration files (Redis, Kvrocks, modules)
tests/               # Unit and integration tests
update/              # Database migration scripts (v5.0 through v6.5)
```

## Core Architecture & Data Flow

### Modular Processing Pipeline

1. **Data Ingestion** → Multiple importers feed data into AIL:
   - ZMQ feeds (external sources)
   - Web/Tor crawlers (via Lacus)
   - MISP imports
   - Pystemon pastebin monitoring
   - Manual file uploads via UI
   - Instance-to-instance sync (AIL-2-AIL)

2. **Message Queue System** → Items enqueued to module processing queues via ZMQ/AILQueue
   - Each item/object gets unique identifiers
   - Tracker system monitors for pattern matches in parallel

3. **Analysis Modules** (run as independent processes):
   - **Base Modules**: Mixer (orchestrator), Global (categorization), Categ, Tags, SubmitPaste
   - **Extraction**: ApiKey, Credential, CreditCards, Keys, Mail, Onion addresses
   - **Processing**: Decoder, Duplicates, Languages, OCR, Exif, CodeReader
   - **Pattern Detection**: Hosts, DomClassifier, IPAddress, IBAN, Phone
   - **Correlation**: Links between decoded files, domains, hashes, crypto addresses, CVEs, titles
   - **Indexing**: Meilisearch full-text search of paste content

4. **Tracking System** (continuous pattern matching):
   - Tracker_Term: keyword/phrase matching
   - Tracker_Regex: regex patterns
   - Tracker_Yara: YARA rules
   - Tracker_Typo_Squatting: domain typos
   - Retro_Hunt: retroactive search across history

5. **Storage & Retrieval**:
   - Redis: caching, module queues, quick lookups
   - Kvrocks: persistent object/relationship data
   - File system: decoded extracts with metadata

6. **Alerting & Export**:
   - MISP export (events)
   - TheHive export (alerts)
   - Email notifications
   - Webhook triggers

7. **Web Interface** (Flask on port 7000):
   - Dashboard, object exploration, search, tracker management
   - Investigation mixer, correlation visualization
   - REST API endpoints (v1)

### Key Abstractions

- **AbstractModule** (bin/modules/abstract_module.py): Base class for all analysis modules with queue processing
- **AIL Objects** (bin/lib/objects/): ORM-like classes for Items, Domains, Credentials, etc.
- **AbstractImporter/AbstractExporter**: Plugin architecture for data sources and destinations
- **ConfigLoader**: Centralized configuration management across all components

## Common Commands

### Starting & Stopping

```bash
# Start AIL (all databases, core services, modules, web interface)
cd bin/
./LAUNCH.sh -l

# Kill all processes
./LAUNCH.sh -k

# Restart
./LAUNCH.sh -r

# Kill only scripts (keep databases running)
./LAUNCH.sh -ks
```

### Testing

```bash
# Run all tests (requires running AIL instance with all services)
cd bin/
./LAUNCH.sh -t

# Run tests directly with nose2
python3 -m nose2 --start-dir ./tests --coverage bin --with-coverage test_api test_modules

# Run specific test
python3 -m nose2 tests.test_modules.TestModuleApiKey
python3 -m nose2 tests.test_api.TestApiV1.test_0001_api_ping
```

### Database Management

```bash
# Check Redis servers status
redis-cli -p 6379 -a ail PING
redis-cli -p 6380 -a ail PING
redis-cli -p 6381 -a ail PING

# Check Kvrocks status
redis-cli -p 6383 -a ail PING

# View Redis keys
redis-cli -p 6379 -a ail KEYS "*"
```

### Configuration & Updates

```bash
# Update AIL (database migrations as needed)
./LAUNCH.sh -u

# Update UI/Frontend dependencies
./LAUNCH.sh -ut

# Reset UI admin password
./LAUNCH.sh -rp

# Advanced menu
./LAUNCH.sh -m
```

### Development Workflow

```bash
# Monitor running modules/services
screen -ls

# Attach to specific service (e.g., check module output)
screen -r Redis_AIL          # Redis servers
screen -r Script_AIL         # Analysis modules
screen -r Flask_AIL          # Web server
screen -r Core_AIL           # Core services
screen -r AIL_2_AIL          # Sync service

# Exit screen session: Ctrl+A, then D

# Check logs (if configured)
tail -f logs/...
```

## Module Development

### Creating a New Analysis Module

1. Extend **AbstractModule** from `bin/modules/abstract_module.py`
2. Implement required methods:
   - `__init__(self)`: Initialize with queue name and configuration
   - `process(self, obj)`: Process individual items from queue
   - `analyze(self, *args)`: Core analysis logic
3. Inherit queue handling, logging, and error management from AbstractModule
4. Add module to `bin/LAUNCH.sh` in the appropriate section
5. Add configuration to `configs/` if needed

### Creating a New Importer

1. Extend **AbstractImporter** from `bin/importer/abstract_importer.py`
2. Implement data source connection and parsing
3. Create Item/Object instances and enqueue them
4. Register in launcher script

### Creating a New Tracker Type

1. Create Python file in `bin/trackers/`
2. Extend tracker base class
3. Implement pattern matching logic
4. Handle matches and notifications (auto-export to MISP/TheHive if configured)

## Important Patterns

### ZMQ Message Queues
- Modules communicate via ZMQ publish-subscribe and request-reply patterns
- Each module has a dedicated input queue from the mixer
- Queue names defined in configuration, typically match module name (lowercase)
- Use `AILQueue` class from `bin/lib/ail_queue.py` for sending messages

### AIL Objects
- Items (pastes), Domains, Credentials, Decodeds, etc. are ORM-like objects
- Objects have relationships (correlations) tracked in Kvrocks
- Objects support tagging with MISP Taxonomies/Galaxies
- Access objects via `from lib.objects import Items, Domains, etc.`

### Configuration
- All configuration via `ConfigLoader()` which reads from `configs/` YAML files
- Database credentials, ports, paths all centrally managed
- Environment: `AIL_HOME`, `AIL_BIN`, `AIL_FLASK` set by LAUNCH.sh

### Logging
- Use `ail_logger` module for consistent logging
- Test logger configured via `ail_logger.get_test_config()`
- Application logger uses configured level from ConfigLoader

## Testing Strategy

- **test_modules.py**: Tests for individual analysis modules (e.g., ApiKey, CreditCards)
  - Uses sample data from `samples/` directory
  - Tests module's ability to extract/identify patterns
- **test_api.py**: Tests Flask API endpoints
  - Requires running Flask server
  - Uses PyAIL client library
  - Tests authentication, item queries, object operations
- Tests run with nose2, can include coverage reports

## Database Architecture Notes

### Redis (3 instances)
- **6379**: Primary cache, general queue operations
- **6380**: Secondary cache, object relationships
- **6381**: Tertiary cache, specialized data structures
- Authentication: password "ail" (from configs/)

### Kvrocks (1 instance, port 6383)
- Persistent storage backend (Redis-compatible API)
- Replaces ARDB in v5.0+
- Stores: AIL objects, relationships, metadata, configuration state
- Survives restarts; Redis instances are ephemeral

### Meilisearch
- Full-text search engine for paste content
- Indexed by Indexer module
- Supports faceted search by date, mime-type, encoding

## Deployment Notes

- AIL uses `screen` for process management (not systemd)
- All modules run as independent Python processes
- Virtual environment at `AILENV/` required before launch
- Installation script: `installing_deps.sh` (Debian/Ubuntu)
- Default web credentials in `DEFAULT_PASSWORD` file (deleted on first password change)
- Supports clustering via AIL-2-AIL sync to other instances

## Debugging Tips

1. **Module not processing**: Check queue name in LAUNCH.sh matches config, verify Redis running
2. **Missing extractions**: Verify module is in LAUNCH.sh and launched without errors
3. **Web interface unreachable**: Check Flask_AIL screen, port 7000 availability
4. **Database migration issues**: Run `LAUNCH.sh -u` to apply pending migrations
5. **Memory issues**: Monitor Redis with `info memory` command, check item queue sizes
6. **Test failures**: Ensure all services running (Redis, Kvrocks, Flask) before running tests

## External Resources

- Documentation: `doc/README.md`
- API Documentation: `doc/api.md`
- HOWTO guides: `HOWTO.md`
- Training materials: https://github.com/ail-project/ail-training
- Main repository: https://github.com/ail-project/ail-framework
