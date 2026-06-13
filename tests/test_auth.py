"""
Testa o sistema de autenticação (frontend/auth.py).
Usa diretório temporário para não modificar data/users.json real.
"""

import pytest
import hashlib
import json
import tempfile
from pathlib import Path
from unittest import mock


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_module_with_tmpdir():
    """Reimporta auth com _DATA_DIR apontando para diretório temporário."""
    import importlib
    import frontend.auth as auth_mod

    tmp = tempfile.mkdtemp()
    original_data_dir  = auth_mod._DATA_DIR
    original_users_file = auth_mod._USERS_FILE

    auth_mod._DATA_DIR   = Path(tmp)
    auth_mod._USERS_FILE = Path(tmp) / "users.json"

    return auth_mod, original_data_dir, original_users_file, tmp


def _restore_module(auth_mod, orig_data_dir, orig_users_file):
    auth_mod._DATA_DIR   = orig_data_dir
    auth_mod._USERS_FILE = orig_users_file


# ── Testes de _hash ───────────────────────────────────────────────────────────

class TestHash:
    def test_hash_is_sha256(self):
        from frontend.auth import _hash
        expected = hashlib.sha256("senha123".encode()).hexdigest()
        assert _hash("senha123") == expected

    def test_same_input_same_hash(self):
        from frontend.auth import _hash
        assert _hash("abc") == _hash("abc")

    def test_different_inputs_different_hashes(self):
        from frontend.auth import _hash
        assert _hash("abc") != _hash("ABC")
        assert _hash("senha1") != _hash("senha2")

    def test_hash_is_64_chars(self):
        from frontend.auth import _hash
        assert len(_hash("qualquer")) == 64

    def test_hash_is_hex(self):
        from frontend.auth import _hash
        h = _hash("test")
        assert all(c in "0123456789abcdef" for c in h)


# ── Testes de register ────────────────────────────────────────────────────────

class TestRegister:
    def setup_method(self):
        import frontend.auth as auth
        self.auth = auth
        self._tmp  = tempfile.mkdtemp()
        self._orig_dir  = auth._DATA_DIR
        self._orig_file = auth._USERS_FILE
        auth._DATA_DIR   = Path(self._tmp)
        auth._USERS_FILE = Path(self._tmp) / "users.json"

    def teardown_method(self):
        self.auth._DATA_DIR   = self._orig_dir
        self.auth._USERS_FILE = self._orig_file

    def test_register_new_user_returns_true(self):
        ok, _ = self.auth.register("joao", "João", "joao@test.com", "senha123")
        assert ok is True

    def test_register_creates_user_in_file(self):
        self.auth.register("maria", "Maria", "maria@test.com", "abc123")
        users = json.loads(self.auth._USERS_FILE.read_text())
        assert "maria" in users

    def test_register_stores_name_and_email(self):
        self.auth.register("ana", "Ana Lima", "ana@test.com", "123456")
        users = json.loads(self.auth._USERS_FILE.read_text())
        assert users["ana"]["name"]  == "Ana Lima"
        assert users["ana"]["email"] == "ana@test.com"

    def test_register_stores_hashed_password(self):
        self.auth.register("bob", "Bob", "bob@test.com", "minhasenha")
        users = json.loads(self.auth._USERS_FILE.read_text())
        expected_hash = hashlib.sha256("minhasenha".encode()).hexdigest()
        assert users["bob"]["password_hash"] == expected_hash

    def test_register_does_not_store_plaintext_password(self):
        self.auth.register("carol", "Carol", "carol@test.com", "segredo")
        users = json.loads(self.auth._USERS_FILE.read_text())
        user_str = json.dumps(users["carol"])
        assert "segredo" not in user_str

    def test_duplicate_username_returns_false(self):
        self.auth.register("dup", "Dup", "dup@test.com", "senha1")
        ok, msg = self.auth.register("dup", "Dup2", "dup2@test.com", "senha2")
        assert ok is False
        assert msg  # mensagem de erro preenchida

    def test_duplicate_email_returns_false(self):
        self.auth.register("u1", "U1", "same@test.com", "s1")
        ok, msg = self.auth.register("u2", "U2", "same@test.com", "s2")
        assert ok is False

    def test_username_normalized_to_lowercase(self):
        self.auth.register("USUARIO", "User", "u@test.com", "pw1234")
        users = json.loads(self.auth._USERS_FILE.read_text())
        assert "usuario" in users
        assert "USUARIO" not in users

    def test_email_normalized_to_lowercase(self):
        self.auth.register("xuser", "X", "X@Test.COM", "pw1234")
        users = json.loads(self.auth._USERS_FILE.read_text())
        assert users["xuser"]["email"] == "x@test.com"

    def test_register_stores_created_at(self):
        self.auth.register("ts", "TS", "ts@t.com", "abcdef")
        users = json.loads(self.auth._USERS_FILE.read_text())
        assert "created_at" in users["ts"]
        assert users["ts"]["created_at"]  # não vazio


# ── Testes de login ───────────────────────────────────────────────────────────

class TestLogin:
    def setup_method(self):
        import frontend.auth as auth
        self.auth = auth
        self._tmp  = tempfile.mkdtemp()
        self._orig_dir  = auth._DATA_DIR
        self._orig_file = auth._USERS_FILE
        auth._DATA_DIR   = Path(self._tmp)
        auth._USERS_FILE = Path(self._tmp) / "users.json"
        # Registra usuário de teste
        auth.register("testuser", "Test User", "test@test.com", "correctpw")

    def teardown_method(self):
        self.auth._DATA_DIR   = self._orig_dir
        self.auth._USERS_FILE = self._orig_file
        # Limpa session_state simulado
        import streamlit as st
        st.session_state.pop("auth", None)

    def test_correct_credentials_return_true(self):
        result = self.auth.login("testuser", "correctpw")
        assert result is True

    def test_wrong_password_returns_false(self):
        result = self.auth.login("testuser", "wrongpw")
        assert result is False

    def test_nonexistent_user_returns_false(self):
        result = self.auth.login("nobody", "anypw")
        assert result is False

    def test_successful_login_sets_session_state(self):
        import streamlit as st
        self.auth.login("testuser", "correctpw")
        assert "auth" in st.session_state
        assert st.session_state.auth["username"] == "testuser"
        assert st.session_state.auth["name"]     == "Test User"
        assert st.session_state.auth["email"]    == "test@test.com"

    def test_failed_login_does_not_set_session_state(self):
        import streamlit as st
        st.session_state.pop("auth", None)
        self.auth.login("testuser", "wrong")
        assert st.session_state.get("auth") is None

    def test_username_case_insensitive(self):
        """Login com 'TestUser' deve funcionar mesmo que foi registrado como 'testuser'."""
        result = self.auth.login("TestUser", "correctpw")
        assert result is True

    def test_empty_password_fails(self):
        result = self.auth.login("testuser", "")
        assert result is False


# ── Testes de is_authenticated ────────────────────────────────────────────────

class TestIsAuthenticated:
    def setup_method(self):
        import streamlit as st
        st.session_state.pop("auth", None)

    def test_unauthenticated_returns_false(self):
        from frontend.auth import is_authenticated
        assert is_authenticated() is False

    def test_after_login_returns_true(self):
        import streamlit as st
        st.session_state.auth = {"username": "u", "name": "N", "email": "e"}
        from frontend.auth import is_authenticated
        assert is_authenticated() is True

    def test_after_clearing_session_returns_false(self):
        import streamlit as st
        st.session_state.auth = {"username": "u", "name": "N", "email": "e"}
        del st.session_state["auth"]
        from frontend.auth import is_authenticated
        assert is_authenticated() is False


# ── Testes de _ensure / inicialização ─────────────────────────────────────────

class TestEnsure:
    def test_ensure_creates_data_dir(self):
        import frontend.auth as auth
        tmp = tempfile.mkdtemp()
        new_dir = Path(tmp) / "new_subdir"
        orig_dir, orig_file = auth._DATA_DIR, auth._USERS_FILE
        auth._DATA_DIR   = new_dir
        auth._USERS_FILE = new_dir / "users.json"
        try:
            auth._ensure()
            assert new_dir.exists()
        finally:
            auth._DATA_DIR   = orig_dir
            auth._USERS_FILE = orig_file

    def test_ensure_creates_users_file(self):
        import frontend.auth as auth
        tmp = tempfile.mkdtemp()
        orig_dir, orig_file = auth._DATA_DIR, auth._USERS_FILE
        auth._DATA_DIR   = Path(tmp)
        auth._USERS_FILE = Path(tmp) / "users.json"
        try:
            auth._ensure()
            assert auth._USERS_FILE.exists()
        finally:
            auth._DATA_DIR   = orig_dir
            auth._USERS_FILE = orig_file

    def test_ensure_includes_demo_user(self):
        import frontend.auth as auth
        tmp = tempfile.mkdtemp()
        orig_dir, orig_file = auth._DATA_DIR, auth._USERS_FILE
        auth._DATA_DIR   = Path(tmp)
        auth._USERS_FILE = Path(tmp) / "users.json"
        try:
            auth._ensure()
            users = json.loads(auth._USERS_FILE.read_text())
            assert "demo" in users
        finally:
            auth._DATA_DIR   = orig_dir
            auth._USERS_FILE = orig_file
