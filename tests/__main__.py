
import unittest
import os.path

if __name__ == '__main__':
    HERE = os.path.dirname(__file__)

    loader = unittest.loader.TestLoader()
    suite = loader.discover(HERE)
    result = unittest.result.TestResult()

    suite.run(result)

    print('Ran {} tests.'.format(result.testsRun))
    print('{} errors, {} failed, {} skipped'.format(
        len(result.errors),
        len(result.failures),
        len(result.skipped),
    ))
    if not result.wasSuccessful():
        if result.errors:
            print('\nErrors:')
            for module, traceback in result.errors:
                print('[{}]\n{}\n\n'.format(module, traceback))
        if result.failures:
            print('\nFailures:')
            for module, traceback in result.failures:
                print('[{}]\n{}\n\n'.format(module, traceback))

