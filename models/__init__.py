from models.base import Base

import models.onboarding.admin_models
import models.onboarding.employee_models
import models.holidays.holiday_models
import models.leaves.leave_request_models
import models.salary_slip.salary_slip_models
import models.location_matrix.location_matrix_models
import models.help_center.help_center_models
import models.notification.notification_models
import models.attendance.attendance_models
import models.break_time.break_time_models
import models.current_location.current_location_models
import models.terms_conditions.terms_conditions_models
import models.privacy_policy.privacy_policy_models
import models.documentation.documentation_models

# This file consolidates all model imports so that Alembic can properly read Base.metadata
