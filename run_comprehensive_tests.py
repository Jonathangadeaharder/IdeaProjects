#!/usr/bin/env python3
"""
Comprehensive test runner for expanded unit test coverage.
Executes both Python ProcessingStep tests and React Native hook tests.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time


class TestRunner:
    """Comprehensive test runner for the entire test suite."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_test_dir = self.project_root / "tests"
        self.rn_test_dir = self.project_root / "EpisodeGameApp" / "tests"
        self.results = {
            "python": {},
            "react_native": {},
            "summary": {}
        }
    
    def run_python_tests(self) -> bool:
        """Run Python unit tests with coverage."""
        print("\n" + "="*60)
        print("RUNNING PYTHON PROCESSING STEP TESTS")
        print("="*60)
        
        try:
            # Change to project root for Python tests
            os.chdir(self.project_root)
            
            # Run basic processing step tests
            print("\n🧪 Running basic ProcessingStep tests...")
            result1 = self._run_python_test_file("test_processing_steps.py")
            
            # Run advanced processing step tests
            print("\n🧪 Running advanced ProcessingStep tests...")
            result2 = self._run_python_test_file("test_processing_steps_advanced.py")
            
            # Run existing granular interface tests
            print("\n🧪 Running granular interface tests...")
            result3 = self._run_python_test_file("test_granular_interfaces.py")
            
            # Run pipeline architecture tests
            print("\n🧪 Running pipeline architecture tests...")
            result4 = self._run_python_test_file("test_pipeline_architecture.py")
            
            # Generate coverage report
            print("\n📊 Generating Python coverage report...")
            self._generate_python_coverage()
            
            all_passed = all([result1, result2, result3, result4])
            self.results["python"]["all_tests_passed"] = all_passed
            
            if all_passed:
                print("\n✅ All Python tests PASSED!")
            else:
                print("\n❌ Some Python tests FAILED!")
            
            return all_passed
            
        except Exception as e:
            print(f"\n❌ Error running Python tests: {e}")
            self.results["python"]["error"] = str(e)
            return False
    
    def run_react_native_tests(self) -> bool:
        """Run React Native hook tests with coverage."""
        print("\n" + "="*60)
        print("RUNNING REACT NATIVE HOOK TESTS")
        print("="*60)
        
        try:
            # Change to React Native project directory
            rn_project_dir = self.project_root / "EpisodeGameApp"
            os.chdir(rn_project_dir)
            
            # Check if node_modules exists
            if not (rn_project_dir / "node_modules").exists():
                print("\n📦 Installing React Native dependencies...")
                self._run_command(["npm", "install"])
            
            # Run basic hook tests
            print("\n🧪 Running basic useGameLogic tests...")
            result1 = self._run_rn_test("tests/hooks/useGameLogic.test.ts")
            
            # Run advanced hook tests
            print("\n🧪 Running advanced useGameLogic tests...")
            result2 = self._run_rn_test("tests/hooks/useGameLogic.advanced.test.ts")
            
            # Run basic processing workflow tests
            print("\n🧪 Running basic useProcessingWorkflow tests...")
            result3 = self._run_rn_test("tests/hooks/useProcessingWorkflow.test.ts")
            
            # Run advanced processing workflow tests
            print("\n🧪 Running advanced useProcessingWorkflow tests...")
            result4 = self._run_rn_test("tests/hooks/useProcessingWorkflow.advanced.test.ts")
            
            # Run existing store tests
            print("\n🧪 Running existing AppStore tests...")
            result5 = self._run_rn_test("tests/stores/AppStore.test.tsx")
            
            # Generate coverage report
            print("\n📊 Generating React Native coverage report...")
            self._generate_rn_coverage()
            
            all_passed = all([result1, result2, result3, result4, result5])
            self.results["react_native"]["all_tests_passed"] = all_passed
            
            if all_passed:
                print("\n✅ All React Native tests PASSED!")
            else:
                print("\n❌ Some React Native tests FAILED!")
            
            return all_passed
            
        except Exception as e:
            print(f"\n❌ Error running React Native tests: {e}")
            self.results["react_native"]["error"] = str(e)
            return False
    
    def _run_python_test_file(self, test_file: str) -> bool:
        """Run a specific Python test file."""
        test_path = self.python_test_dir / test_file
        
        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_path}")
            return False
        
        try:
            # Run with unittest discovery
            cmd = [sys.executable, "-m", "unittest", f"tests.{test_file[:-3]}", "-v"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                self._parse_python_test_output(test_file, result.stdout)
                return True
            else:
                print(f"❌ {test_file} - FAILED")
                print(f"Error output: {result.stderr}")
                self.results["python"][test_file] = {
                    "status": "failed",
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ {test_file} - ERROR: {e}")
            return False
    
    def _run_rn_test(self, test_file: str) -> bool:
        """Run a specific React Native test file."""
        try:
            # Use Jest to run specific test file
            cmd = ["npx", "jest", test_file, "--verbose", "--no-cache"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                self._parse_rn_test_output(test_file, result.stdout)
                return True
            else:
                print(f"❌ {test_file} - FAILED")
                print(f"Error output: {result.stderr}")
                self.results["react_native"][test_file] = {
                    "status": "failed",
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ {test_file} - ERROR: {e}")
            return False
    
    def _run_command(self, cmd: List[str]) -> bool:
        """Run a shell command."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except Exception:
            return False
    
    def _parse_python_test_output(self, test_file: str, output: str):
        """Parse Python test output to extract test counts."""
        lines = output.split('\n')
        test_count = 0
        for line in lines:
            if 'test_' in line and ('ok' in line.lower() or 'passed' in line.lower()):
                test_count += 1
        
        self.results["python"][test_file] = {
            "status": "passed",
            "test_count": test_count
        }
    
    def _parse_rn_test_output(self, test_file: str, output: str):
        """Parse React Native test output to extract test counts."""
        lines = output.split('\n')
        test_count = 0
        for line in lines:
            if '✓' in line or 'PASS' in line:
                test_count += 1
        
        self.results["react_native"][test_file] = {
            "status": "passed",
            "test_count": test_count
        }
    
    def _generate_python_coverage(self):
        """Generate Python coverage report."""
        try:
            # Install coverage if not available
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], 
                         capture_output=True)
            
            # Run tests with coverage
            subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "unittest", 
                          "discover", "-s", "tests", "-p", "test_*.py"], 
                         capture_output=True)
            
            # Generate coverage report
            result = subprocess.run([sys.executable, "-m", "coverage", "report"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("\n📊 Python Coverage Report:")
                print(result.stdout)
                self.results["python"]["coverage"] = result.stdout
            
        except Exception as e:
            print(f"⚠️  Could not generate Python coverage: {e}")
    
    def _generate_rn_coverage(self):
        """Generate React Native coverage report."""
        try:
            # Run Jest with coverage
            result = subprocess.run(["npx", "jest", "--coverage", "--coverageDirectory=coverage"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("\n📊 React Native Coverage Report:")
                print(result.stdout)
                self.results["react_native"]["coverage"] = result.stdout
            
        except Exception as e:
            print(f"⚠️  Could not generate React Native coverage: {e}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        # Python summary
        python_passed = self.results["python"].get("all_tests_passed", False)
        python_test_count = sum(
            result.get("test_count", 0) 
            for key, result in self.results["python"].items() 
            if isinstance(result, dict) and "test_count" in result
        )
        
        print(f"\n🐍 Python Tests:")
        print(f"   Status: {'✅ PASSED' if python_passed else '❌ FAILED'}")
        print(f"   Total Tests: {python_test_count}")
        
        # React Native summary
        rn_passed = self.results["react_native"].get("all_tests_passed", False)
        rn_test_count = sum(
            result.get("test_count", 0) 
            for key, result in self.results["react_native"].items() 
            if isinstance(result, dict) and "test_count" in result
        )
        
        print(f"\n⚛️  React Native Tests:")
        print(f"   Status: {'✅ PASSED' if rn_passed else '❌ FAILED'}")
        print(f"   Total Tests: {rn_test_count}")
        
        # Overall summary
        overall_passed = python_passed and rn_passed
        total_tests = python_test_count + rn_test_count
        
        print(f"\n🎯 Overall Summary:")
        print(f"   Status: {'✅ ALL TESTS PASSED' if overall_passed else '❌ SOME TESTS FAILED'}")
        print(f"   Total Tests: {total_tests}")
        print(f"   Python Tests: {python_test_count}")
        print(f"   React Native Tests: {rn_test_count}")
        
        # Save results to file
        self.results["summary"] = {
            "overall_passed": overall_passed,
            "total_tests": total_tests,
            "python_tests": python_test_count,
            "react_native_tests": rn_test_count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        results_file = self.project_root / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return overall_passed
    
    def run_all_tests(self) -> bool:
        """Run all tests and generate comprehensive report."""
        print("🚀 Starting comprehensive test suite...")
        start_time = time.time()
        
        # Run Python tests
        python_success = self.run_python_tests()
        
        # Run React Native tests
        rn_success = self.run_react_native_tests()
        
        # Generate summary
        overall_success = self.generate_summary_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  Total execution time: {duration:.2f} seconds")
        
        if overall_success:
            print("\n🎉 All tests completed successfully!")
            print("\n📈 Unit test coverage has been significantly expanded for:")
            print("   • Python ProcessingStep classes (basic + advanced scenarios)")
            print("   • React Native hooks (useGameLogic + useProcessingWorkflow)")
            print("   • Error handling and edge cases")
            print("   • Performance and memory management")
            print("   • Integration scenarios")
        else:
            print("\n⚠️  Some tests failed. Please review the output above.")
        
        return overall_success


def main():
    """Main entry point."""
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()