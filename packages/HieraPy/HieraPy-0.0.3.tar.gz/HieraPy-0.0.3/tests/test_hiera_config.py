import sys
import os

from chai import Chai

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from hierapy import HieraPy

single_config = {
    ':hierarchy': ['base'],
}
overriden_config = {
    ':hierarchy': ['override', 'base'],
}
config_base = {
    'login': 'username',
    'password': 'secret',
    'deep': {
        'inner': 'deep-value',
        'way-deeper': {
            'most' : [
                'assorted',
                'values',
            ]
        },
    },
}
config_override = {
    'login': 'username',
    'password': 'overridden',
    'extra': 'extra-value',
    'deep': {
        'inner': 'other-deep-value',
    },
}

class TestHieraConfig(Chai):

    def test_getWithSingleConfig(self):
        config = self._get_mocked_config(
            HieraPy('single.yaml', 'folder')
        )
        assert_equals('username', config.get('login'))
        assert_equals('secret', config.get('password'))
        assert_false(config.get('extra'))

    def test_getWithOverriddenConfig(self):
        config = self._get_mocked_config(
            HieraPy('overriden.yaml', 'folder'),
            True
        )
        assert_equals('username', config.get('login'))
        assert_equals('overridden', config.get('password'))
        assert_equals('extra-value', config.get('extra'))

    def test_getGetDefaultValues(self):
        config = self._get_mocked_config(
            HieraPy('single.yaml', 'folder')
        )
        assert_false(config.get('non-existent'))
        assert_equals(
            'expected-default',
            config.get('non-existent', 'expected-default')
        )

    def test_getGetDeepValues(self):
        config = self._get_mocked_config(
            HieraPy('single.yaml', 'folder')
        )
        assert_equals('deep-value', config.get('deep/inner'))
        assert_equals(
            ['assorted', 'values'],
            config.get('deep/way-deeper/most'))

    def _get_mocked_config(self, config, include_override = False):
        loader = mock()
        if include_override:
            expect(loader).args('overriden.yaml').returns(overriden_config)
            expect(loader).args('folder/base.yaml').returns(config_base)
            expect(loader).args('folder/override.yaml').returns(config_override)
        else:
            expect(loader).args('single.yaml').returns(single_config)
            expect(loader).args('folder/base.yaml').returns(config_base)
        config._HieraPy__load = loader
        return config

if __name__ == '__main__':
    import unittest2
    unittest2.main()
