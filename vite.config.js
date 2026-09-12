import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

// Loopback-only, development-only evidence sink. No uploads leave this computer.
export default defineConfig({
  server: { host: '127.0.0.1', port: 5173, strictPort: true,
    watch: { ignored: ['**/Unity/**', '**/ArtSource/**', '**/.dream-loop/**', '**/Migration/**'] } },
  plugins: [{ name: 'dream-loop-evidence', configureServer(server) {
    server.middlewares.use('/__qa', (req, res) => {
      if (req.method !== 'POST') { res.statusCode = 405; res.end(); return; }
      const origin = req.headers.origin;
      if (origin && origin !== 'http://127.0.0.1:5173' && origin !== 'http://localhost:5173') { res.statusCode = 403; res.end(); return; }
      let body = ''; req.on('data', c => { body += c; if (body.length > 20e6) req.destroy(); });
      req.on('end', () => { try {
        const data = JSON.parse(body); const dir = path.resolve('.dream-loop/evidence'); fs.mkdirSync(dir, { recursive: true });
        const label = String(data.label || 'capture').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 60);
        if (data.image) fs.writeFileSync(path.join(dir, `${label}.png`), Buffer.from(data.image.split(',')[1], 'base64'));
        fs.writeFileSync(path.join(dir, `${label}.json`), JSON.stringify(data.metrics || data, null, 2));
        res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify({ saved: label }));
      } catch { res.statusCode = 400; res.end('Invalid evidence'); } });
    });
  } }],
});
