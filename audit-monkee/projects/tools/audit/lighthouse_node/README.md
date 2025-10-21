# Lighthouse Node Runner

## Install
```bash
cd projects/tools/audit/lighthouse_node
npm i
```

## Run
```bash
node run.js https://example.com > out.json
```

This prints the Lighthouse JSON (`lhr`) to stdout. The Python worker can call this and parse the result.
