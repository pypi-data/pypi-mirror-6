# -*- coding: utf-8 -*-
"""
Tests the hyper window manager.
"""
from hyper.http20.window import BaseFlowControlManager, FlowControlManager
import pytest

class TestBaseFCM(object):
    """
    Tests the base flow control manager.
    """
    def test_base_manager_stores_data(self):
        b = BaseFlowControlManager(65535)
        assert b.initial_window_size == 65535
        assert b.window_size == 65535
        assert b.document_size is None

    def test_base_manager_stores_document_size(self):
        b = BaseFlowControlManager(0, 650)
        assert b.document_size == 650

    def test_base_manager_doesnt_function(self):
        b = BaseFlowControlManager(10, 10)
        with pytest.raises(NotImplementedError):
            b.increase_window_size(10)

    def test_base_manager_private_interface_doesnt_function(self):
        b = BaseFlowControlManager(10, 10)
        with pytest.raises(NotImplementedError):
            b._handle_frame(10)

    def test_base_manager_decrements_window_size(self):
        class TestFCM(BaseFlowControlManager):
            def increase_window_size(self, frame_size):
                pass

        b = TestFCM(10, 10)
        b._handle_frame(5)
        assert b.initial_window_size == 10
        assert b.window_size == 5
        assert b.document_size == 10


class TestFCM(object):
    """
    Test's hyper's build-in Flow-Control Manager.
    """
    def test_fcm_returns_whats_given(self):
        b = FlowControlManager(100, 100)
        assert b._handle_frame(10) == 10
        assert b._handle_frame(30) == 30
        assert b.window_size == 60
