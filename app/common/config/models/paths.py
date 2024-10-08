from pathlib import Path

from pydantic import BaseModel, DirectoryPath


class Paths(BaseModel):
    base_dir: DirectoryPath = (
        Path(__file__).resolve().parent.parent.parent.parent.parent
    )
    app_dir: DirectoryPath = base_dir / "app"
    data_dir: DirectoryPath = base_dir / "data"
    file_dir: DirectoryPath = base_dir / "files"

    @property
    def field_replace(self):
        return self.data_dir / "field_replace.csv"

    @property
    def reservoir_replace(self):
        return self.data_dir / "reservoir_replace.csv"

    @property
    def layer_replace(self):
        return self.data_dir / "layer_replace.csv"

    @property
    def gtm_replace(self):
        return self.data_dir / "gtm_replace.csv"

    @property
    def monthly_report(self):
        return self.data_dir / "monthly_report.csv"

    @property
    def well_profile(self):
        return self.data_dir / "well_profile.csv"

    @property
    def inj_well_database(self):
        return self.data_dir / "inj_well_database.csv"

    @property
    def neighborhood(self):
        return self.data_dir / "neighborhood.csv"

    @property
    def new_strategy_inj(self):
        return self.data_dir / "new_strategy_inj.csv"

    @property
    def new_strategy_oil(self):
        return self.data_dir / "new_strategy_oil.csv"

    @property
    def report_config(self):
        return self.app_dir / "api" / "config" / "yaml" / "reports.yaml"

    @property
    def table_config(self):
        return self.app_dir / "api" / "config" / "yaml" / "tables.yaml"

    @property
    def mmb_config(self):
        return self.app_dir / "core" / "config" / "yaml" / "mmb.yaml"
