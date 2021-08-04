from django.db import models
from jsonfield import JSONField


class Lifecycle(models.Model):
    name = models.CharField(max_length=15, null=False)
    lifecycle = JSONField(null=False)

    def next_state_is_valid(self, current_state, new_state):
        state_obj = self.lifecycle.get(current_state)
        if state_obj is None:
            raise ValueError(f"Incorrect state '{current_state}' "
                             f"for lifecycle {self.name}!")

        # can't change the final state
        if state_obj.get("final", False):
            return False

        # can only change to valid states
        allowed_states = state_obj["next"]
        if new_state not in allowed_states:
            return False

        return True

    def save(self, *args, **kwargs):
        # validate new lifecycle
        default_count = 0
        has_initial = False
        if not self.lifecycle:
            raise ValueError("Empty lifecycle!")

        for status, vals in self.lifecycle.items():
            is_orphan = True
            if vals.get("initial", False):
                has_initial = True
            if vals.get("default", False):
                default_count += 1
            for s, v in self.lifecycle.items():
                if status in v.get("next", []):
                    is_orphan = False
                    break

            if is_orphan:
                raise ValueError(f"Status '{status}' is orphaned")

        if default_count == 0:
            raise ValueError("New lifecycle has no default status")
        elif default_count > 1:
            raise ValueError("New lifecycle has more than one default statuses")
        if not has_initial:
            raise ValueError("New lifecycle has no initial statuses")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
