"""
Unit tests for BaseRepository
Tests the abstract base repository pattern
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.repository.base_repository import BaseRepository


class ModelForRepositoryTesting:
    """Simple test model for repository testing"""
    def __init__(self, id=None, name="", value=""):
        self.id = id
        self.name = name
        self.value = value


class ConcreteTestRepository(BaseRepository[ModelForRepositoryTesting]):
    """Concrete implementation of BaseRepository for testing"""

    @property
    def table_name(self) -> str:
        return "test_table"

    @property
    def model_class(self):
        return ModelForRepositoryTesting
    
    def _row_to_model(self, row: Dict[str, Any]) -> ModelForRepositoryTesting:
        return ModelForRepositoryTesting(
            id=row.get('id'),
            name=row.get('name', ''),
            value=row.get('value', '')
        )
    
    def _model_to_dict(self, model: ModelForRepositoryTesting) -> Dict[str, Any]:
        return {
            'id': model.id,
            'name': model.name,
            'value': model.value
        }


class TestBaseRepository:
    """Test suite for BaseRepository abstract class"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager for testing"""
        from unittest.mock import MagicMock
        mock_db = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()

        # Setup connection and cursor mocks
        mock_conn.cursor.return_value = mock_cursor

        # Setup context manager properly
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_conn
        mock_context_manager.__exit__.return_value = None
        mock_db.get_connection.return_value = mock_context_manager

        return mock_db, mock_conn, mock_cursor
    
    @pytest.fixture
    def repository(self, mock_db_manager):
        """Create concrete repository with mocked database"""
        mock_db, _, _ = mock_db_manager
        return ConcreteTestRepository()
    
    @pytest.fixture
    def sample_model(self):
        """Sample model for testing"""
        return ModelForRepositoryTesting(id=1, name="test", value="sample")
    
    def test_table_name_property(self, repository):
        """Test table name property is implemented"""
        assert repository.table_name == "test_table"
    
    async def test_find_by_id_with_dict_row(self, repository, mock_db_manager):
        """Test find_by_id when database returns dictionary row"""
        _, mock_conn, mock_cursor = mock_db_manager

        # Mock database response as dictionary
        mock_row = {'id': 1, 'name': 'test', 'value': 'sample'}
        mock_cursor.fetchone.return_value = mock_row

        # Mock isinstance check for dict
        with patch('builtins.isinstance', side_effect=lambda obj, cls: cls == dict):
            result = await repository.find_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "test"
        assert result.value == "sample"
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table WHERE id = ?", (1,))
    
    async def test_find_by_id_with_sqlite_row(self, repository, mock_db_manager):
        """Test find_by_id when database returns sqlite3.Row object"""
        _, mock_conn, mock_cursor = mock_db_manager

        # Mock sqlite3.Row-like object
        mock_row = Mock()
        mock_row.keys.return_value = ['id', 'name', 'value']
        mock_row.__getitem__ = lambda self, key: {'id': 1, 'name': 'test', 'value': 'sample'}[key]
        mock_cursor.fetchone.return_value = mock_row

        # Mock dict() conversion and isinstance checks
        with patch('builtins.dict', return_value={'id': 1, 'name': 'test', 'value': 'sample'}):
            with patch('builtins.isinstance', return_value=False):  # Not dict, not _asdict
                result = await repository.find_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.name == "test"
    
    async def test_find_all_with_pagination(self, repository, mock_db_manager):
        """Test find_all with limit and offset"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        mock_rows = [
            {'id': 1, 'name': 'test1', 'value': 'sample1'},
            {'id': 2, 'name': 'test2', 'value': 'sample2'}
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        with patch('builtins.isinstance', side_effect=lambda obj, cls: cls == dict):
            results = await repository.find_all(limit=10, offset=5)
        
        assert len(results) == 2
        assert results[0].id == 1
        assert results[1].id == 2
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table LIMIT ? OFFSET ?", [10, 5])
    
    async def test_find_all_without_pagination(self, repository, mock_db_manager):
        """Test find_all without pagination parameters"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        mock_rows = [{'id': 1, 'name': 'test', 'value': 'sample'}]
        mock_cursor.fetchall.return_value = mock_rows
        
        with patch('builtins.isinstance', side_effect=lambda obj, cls: cls == dict):
            results = await repository.find_all()
        
        assert len(results) == 1
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table", [])
    
    async def test_find_by_criteria_with_conditions(self, repository, mock_db_manager):
        """Test find_by_criteria with search conditions"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        criteria = {'name': 'test', 'value': 'sample'}
        mock_rows = [{'id': 1, 'name': 'test', 'value': 'sample'}]
        mock_cursor.fetchall.return_value = mock_rows
        
        with patch('builtins.isinstance', side_effect=lambda obj, cls: cls == dict):
            results = await repository.find_by_criteria(criteria)
        
        assert len(results) == 1
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test_table WHERE name = ? AND value = ?",
            ['test', 'sample']
        )
    
    async def test_find_by_criteria_empty_criteria(self, repository, mock_db_manager):
        """Test find_by_criteria with empty criteria returns find_all"""
        with patch.object(repository, 'find_all', return_value=[]) as mock_find_all:
            results = await repository.find_by_criteria({})
        
        mock_find_all.assert_called_once()
        assert results == []
    
    async def test_save_new_entity_insert(self, repository, mock_db_manager, sample_model):
        """Test saving new entity (insert operation)"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        
        # New entity without ID
        sample_model.id = None
        mock_cursor.lastrowid = 5
        
        # Mock transaction context manager
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = await repository.save(sample_model)
        
        assert result.id == 5
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ['test', 'sample']
        )
    
    async def test_save_existing_entity_update(self, repository, mock_db_manager, sample_model):
        """Test saving existing entity (update operation)"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        
        # Existing entity with ID
        sample_model.id = 1
        
        # Mock transaction context manager
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = await repository.save(sample_model)
        
        assert result.id == 1
        mock_cursor.execute.assert_called_once_with(
            "UPDATE test_table SET name = ?, value = ? WHERE id = ?",
            ['test', 'sample', 1]
        )
    
    async def test_delete_by_id_success(self, repository, mock_db_manager):
        """Test successful deletion by ID"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.rowcount = 1
        
        # Mock transaction context manager
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = await repository.delete_by_id(1)
        
        assert result is True
        mock_cursor.execute.assert_called_once_with("DELETE FROM test_table WHERE id = ?", (1,))
    
    async def test_delete_by_id_not_found(self, repository, mock_db_manager):
        """Test deletion when entity doesn't exist"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.rowcount = 0
        
        # Mock transaction context manager
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = await repository.delete_by_id(999)
        
        assert result is False
    
    async def test_count_with_criteria(self, repository, mock_db_manager):
        """Test counting entities with criteria"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (3,)
        
        count = await repository.count({"name": "test"})
        
        assert count == 3
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM test_table WHERE name = ?",
            ["test"]
        )
    
    async def test_count_without_criteria(self, repository, mock_db_manager):
        """Test counting all entities"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (10,)
        
        count = await repository.count()
        
        assert count == 10
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM test_table")
    
    async def test_execute_raw_query(self, repository, mock_db_manager):
        """Test executing raw SQL query"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        mock_rows = [{'id': 1, 'name': 'test'}]
        mock_cursor.fetchall.return_value = mock_rows
        
        with patch('builtins.isinstance', side_effect=lambda obj, cls: cls == dict):
            results = await repository.execute_raw_query("SELECT * FROM test_table WHERE name = ?", ("test",))
        
        assert len(results) == 1
        assert results[0] == {'id': 1, 'name': 'test'}
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table WHERE name = ?", ("test",))
    
    async def test_transaction_fallback_without_transaction_method(self, repository, mock_db_manager):
        """Test transaction fallback when db_manager doesn't have transaction method"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        
        # Remove transaction method to test fallback
        del mock_db.transaction
        
        sample_model = ModelForRepositoryTesting(id=None, name="test", value="sample")
        mock_cursor.lastrowid = 5
        
        result = await repository.save(sample_model)
        
        assert result.id == 5
        mock_conn.commit.assert_called_once()
    
    async def test_error_handling_connection_error(self, repository, mock_db_manager):
        """Test error handling when database connection fails"""
        mock_db, _, _ = mock_db_manager
        mock_db.get_connection.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            await repository.find_by_id(1)
    
    async def test_error_handling_transaction_error(self, repository, mock_db_manager):
        """Test error handling when transaction fails"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.execute.side_effect = Exception("Transaction failed")

        # Mock transaction context manager
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)

        sample_model = ModelForRepositoryTesting(name="test", value="sample")

        with pytest.raises(Exception, match="Transaction failed"):
            await repository.save(sample_model)
