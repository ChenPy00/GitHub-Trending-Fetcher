```json
{
  "owner": "Stremio",
  "name": "stremio-web",
  "full_name": "Stremio/stremio-web",
  "url": "https://github.com/Stremio/stremio-web",
  "description": "Stremio - Freedom to Stream",
  "readme_sha256": "c2157ed46421a212da11f91351cd7cf106c9d04fdf29ea19f8d2be5175770aaf"
}
```

# Stremio/stremio-web

- URL: https://github.com/Stremio/stremio-web
- Description: Stremio - Freedom to Stream
- README SHA256: `c2157ed46421a212da11f91351cd7cf106c9d04fdf29ea19f8d2be5175770aaf`

## README

# Stremio - Freedom to Stream

[![Build](https://github.com/Stremio/stremio-web/actions/workflows/build.yml/badge.svg)](https://github.com/Stremio/stremio-web/actions/workflows/build.yml)
[![Github Page](https://img.shields.io/website?label=Page&logo=github&up_message=online&down_message=offline&url=https%3A%2F%2Fstremio.github.io%2Fstremio-web%2F)](https://stremio.github.io/stremio-web/development)

Stremio is a modern media center that's a one-stop solution for your video entertainment. You discover, watch and organize video content from easy to install addons.

## Build

### Prerequisites

* Node.js 12 or higher
* [pnpm](https://pnpm.io/installation) 10 or higher

### Install dependencies

```bash
pnpm install
```

### Start development server

```bash
pnpm start
```

### Production build

```bash
pnpm run build
```

### Run with Docker

```bash
docker build -t stremio-web .
docker run -p 8080:8080 stremio-web
```

## Screenshots

### Board

![Board](/assets/screenshots/board.png)

### Discover

![Discover](/assets/screenshots/discover.png)

### Meta Details

![Meta Details](/assets/screenshots/metadetails.png)

## License

Stremio is copyright 2017-2023 Smart code and available under GPLv2 license. See the [LICENSE](/LICENSE.md) file in the project for more information.
