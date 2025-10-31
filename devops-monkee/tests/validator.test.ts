import { Validator } from '../src/governance/validator';
import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';

describe('Validator', () => {
  let validator: Validator;
  let tempDir: string;

  beforeEach(async () => {
    validator = new Validator();
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'sbep-test-'));
  });

  afterEach(async () => {
    await fs.remove(tempDir);
  });

  describe('validate', () => {
    it('should validate a compliant project structure', async () => {
      // Create minimal compliant structure
      await fs.ensureDir(path.join(tempDir, 'sds'));
      await fs.writeFile(path.join(tempDir, 'sds', 'SBEP-MANDATE.md'), '# Test Mandate\n');
      await fs.writeFile(path.join(tempDir, 'sds', 'SBEP-INDEX.yaml'), 'title: "Test Index"\n');
      await fs.writeFile(path.join(tempDir, 'README.md'), '# Test Project\n');
      await fs.writeFile(path.join(tempDir, 'CHANGELOG.md'), '# Changelog\n');

      const result = await validator.validate(tempDir);

      expect(result.score).toBeGreaterThan(0);
      expect(result.issues.length).toBeGreaterThan(0); // Will have some issues due to missing files
    });

    it('should identify missing required files', async () => {
      const result = await validator.validate(tempDir);

      const criticalIssues = result.issues.filter(issue => issue.severity === 'critical');
      expect(criticalIssues.length).toBeGreaterThan(0);
      expect(criticalIssues.some(issue => issue.message.includes('missing'))).toBe(true);
    });

    it('should generate recommendations for issues', async () => {
      const result = await validator.validate(tempDir);

      expect(result.recommendations).toBeDefined();
      expect(Array.isArray(result.recommendations)).toBe(true);
      expect(result.recommendations.length).toBeGreaterThan(0);
    });
  });

  describe('calculateGrade', () => {
    it('should assign correct grades based on scores', async () => {
      expect(await validator['calculateGrade'](95)).toBe('A');
      expect(await validator['calculateGrade'](85)).toBe('B');
      expect(await validator['calculateGrade'](75)).toBe('C');
      expect(await validator['calculateGrade'](65)).toBe('D');
      expect(await validator['calculateGrade'](45)).toBe('F');
    });
  });
});
