import { dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Minimal ESLint config - avoids FlatCompat circular reference
// and @typescript-eslint plugin resolution issues
const eslintConfig = [
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: "module",
    },
  },
  {
    rules: {
      "no-console": "warn",
    },
  },
];

export default eslintConfig;