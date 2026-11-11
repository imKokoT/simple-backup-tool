import pytest
import os
from pathlib import Path
from io import BytesIO
from unittest.mock import MagicMock, patch

from src.core.vfs import VirtualFS, VFile, size, exists


@pytest.fixture(autouse=True)
def reset_vfs():
    """Resets the class-level dictionaries in VirtualFS before each test"""
    VirtualFS._opened = {}
    VirtualFS._vfs = {}
    VirtualFS._lastOpenedLocation = {}
    yield

@pytest.fixture
def vfs():
    return VirtualFS()

@pytest.fixture
def mock_config(monkeypatch):
    """
    Mocks the entire config object.
    Returns a MagicMock where the .get() method can be controlled.
    """
    mock_cfg = MagicMock()    
    monkeypatch.setattr("src.core.vfs.config", mock_cfg)
    return mock_cfg


class TestVirtualFS:

    # --- Tests for get() ---

    def test_get_opened_file(self, vfs):
        path = Path("test_file.bin")
        vf = VFile(path, mode='w', location='ram')
        assert vfs.get(path) == vf
        vf.close()
        assert vfs.get(path) is None

    def test_get_non_existent(self, vfs):
        assert vfs.get(Path("non_existent")) is None

    # --- Tests for free() ---

    def test_free_ram_file(self, vfs):
        path = Path("temp_ram.bin")
        vf = VFile(path, mode='w', location='ram')
        vf.close()
        vfs.free(path)
        assert path not in vfs._vfs
        assert path not in vfs._opened

    def test_free_disk_file(self, vfs, tmp_path):
        path = tmp_path / "temp_disk.bin"
        vf = VFile(path, mode='w', location='disk')
        vf.close()
        vfs.free(path)
        # After free, the physical file might still exist depending on OS, 
        # but it should definitely be removed from VFS tracking
        assert path not in vfs._vfs

    def test_free_unclosed_file_raises_error(self, vfs):
        path = Path("active.bin")
        VFile(path, mode='w', location='ram')
        with pytest.raises(ValueError, match='not closed'):
            vfs.free(path)

    # --- Tests for parity: RAM vs DISK ---

    @pytest.mark.parametrize("location", ["ram", "disk"])
    def test_read_write_parity(self, location, tmp_path):
        """Tests that writing and reading works identically in both modes."""
        path = tmp_path / "parity.bin" if location == "disk" else Path("parity_ram.bin")
        data = b"testing data"
        
        # Write
        vf_w = VFile(path, mode='w', location=location)
        vf_w.write(data)
        vf_w.close()

        # Read
        vf_r = VFile(path, mode='r', location=location)
        assert vf_r.read() == data
        vf_r.close()

        # Cleanup if disk
        if location == "disk":
            from src.core.vfs import vfs as global_vfs
            global_vfs.free(path)
            if path.exists(): os.remove(path)
        else:
            from src.core.vfs import vfs as global_vfs
            global_vfs.free(path)

    @pytest.mark.parametrize("location", ["ram", "disk"])
    def test_size_function_parity(self, location, tmp_path):
        path = tmp_path / "size_test.bin" if location == "disk" else Path("size_ram.bin")
        content = b"12345"
        
        vf = VFile(path, mode='w', location=location)
        vf.write(content)
        vf.close()

        assert size(path) == 5
        assert exists(path) is True

        from src.core.vfs import vfs as global_vfs
        global_vfs.free(path)

    # --- Tests for _onOpen() / Error States ---

    def test_prevent_double_open_same_path(self):
        path = Path("double_open.bin")
        vf1 = VFile(path, mode='r', location='ram')
        with pytest.raises(RuntimeError, match="already opened"):
            VFile(path, mode='r', location='ram')
        vf1.close()
        from src.core.vfs import vfs as global_vfs
        global_vfs.free(path)

    def test_prevent_ram_disk_collision(self, tmp_path):
        """Tests that you cannot open a disk file if it is already in RAM."""
        path = tmp_path / "collision.bin"
        # 1. Put it in RAM
        vf_ram = VFile(path, mode='w', location='ram')
        vf_ram.close()
        
        # 2. Try to open same path as DISK
        with pytest.raises(RuntimeError, match="cannot open VFile on disk while it exists in-memory"):
            VFile(path, mode='r', location='disk')
        
        from src.core.vfs import vfs as global_vfs
        global_vfs.free(path)

    def test_zero_waste_config_logic(self, monkeypatch, tmp_path):
        """Tests that 'zero_waste' config correctly defaults location"""
        mock_config = MagicMock()
        monkeypatch.setattr("src.core.vfs.config", mock_config)
        
        # Case 1: zero_waste = True -> RAM
        mock_config.get.return_value = True
        vf_ram = VFile(Path("waste_ram.bin"), location=None)
        assert vf_ram._location == 'ram'
        vf_ram.close()
        from src.core.vfs import vfs as global_vfs
        global_vfs.free(Path("waste_ram.bin"))

        # Case 2: zero_waste = False -> DISK
        mock_config.get.return_value = False
        # Create an dummy file
        disk_path = tmp_path / "waste_disk.bin"
        disk_path.touch() 
        
        vf_disk = VFile(disk_path, mode='r', location=None)
        assert vf_disk._location == 'disk'
        vf_disk.close()
        global_vfs.free(disk_path)

    # --- Tests for _onClose() ---

    def test_on_close(self):
        """Tests that closing a RAM file leaves the buffer at seek(0) for reuse."""
        path = Path("seek_test.bin")
        vf = VFile(path, mode='w', location='ram')
        vf.write(b"data")
        vf.close()
        
        # Re-open (vfs._onClose should have seeked to 0)
        vf2 = VFile(path, mode='r', location='ram')
        assert vf2.read() == b"data"
        vf2.close()
        from src.core.vfs import vfs as global_vfs
        global_vfs.free(path)    
