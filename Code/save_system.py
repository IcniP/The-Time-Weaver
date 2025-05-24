import json
import os
from typing import Dict, List, Optional, Tuple

"""save_system.py – v3

• Gunakan folder ./saves/ otomatis.
• Field *level* opsional (tidak crash kalau objek player tidak punya atribut itu).
• Validasi load cukup cek kunci wajib: checkpoint, position, hp, stamina.
"""

class SaveManager:
    SAVE_DIR = "saves"
    FILE_TEMPLATE = "slot{slot}.json"

    # ────────────────────── helpers ──────────────────────
    @staticmethod
    def _ensure_dir() -> None:
        os.makedirs(SaveManager.SAVE_DIR, exist_ok=True)

    @staticmethod
    def _slot_path(slot: int) -> str:
        return os.path.join(SaveManager.SAVE_DIR,
                            SaveManager.FILE_TEMPLATE.format(slot=slot))

    # ────────────────────── API ───────────────────────────
    @staticmethod
    def save_game(player, checkpoint: str, slot: int = 1) -> None:
        """Simpan state player ke file slot<n>.json."""
        SaveManager._ensure_dir()

        data: Dict = {
            "checkpoint": checkpoint,                      # id map / stage
            "position":  list(player.rect.topleft),       # where the player stands
            "hp":        int(getattr(player, "hp", 0)),
            "stamina":   int(getattr(player, "stamina", 0)),
        }
        lvl = getattr(player, "level", None)
        if lvl is not None:
            data["level"] = int(lvl)

        with open(SaveManager._slot_path(slot), "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)

    @staticmethod
    def load_game(slot: int = 1) -> Optional[Dict]:
        path = SaveManager._slot_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            must_have = {"checkpoint", "position", "hp", "stamina"}
            return data if must_have.issubset(data) else None
        except (OSError, json.JSONDecodeError):
            return None

    @staticmethod
    def delete_save(slot: int) -> bool:
        try:
            os.remove(SaveManager._slot_path(slot))
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def list_saves() -> List[Tuple[int, Dict]]:
        SaveManager._ensure_dir()
        result: List[Tuple[int, Dict]] = []
        for fname in os.listdir(SaveManager.SAVE_DIR):
            if fname.startswith("slot") and fname.endswith(".json"):
                try:
                    slot = int(fname[4:-5])
                except ValueError:
                    continue
                data = SaveManager.load_game(slot)
                if data:
                    result.append((slot, data))
        result.sort(key=lambda t: t[0])
        return result

    @staticmethod
    def get_player_level(slot: int) -> Optional[int]:
        data = SaveManager.load_game(slot)
        return data.get("level") if data else None


if __name__ == "__main__":
    class _Mock:
        def __init__(self):
            self.rect = type("rect", (), {"topleft": (123, 456)})
            self.hp = 3
            self.stamina = 2
    p = _Mock()
    SaveManager.save_game(p, checkpoint="3-0", slot=1)
    print("saved")
    print(SaveManager.load_game(1))