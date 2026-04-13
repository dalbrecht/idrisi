#!/usr/bin/env node
// Copies docs/about/naming.md into site/src/content/naming.md so Astro
// can import it. Run as site's prebuild step.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "..", "..", "docs", "about", "naming.md");
const dest = resolve(here, "..", "src", "content", "naming.md");

mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log(`copied ${src} → ${dest}`);
