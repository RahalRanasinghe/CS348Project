-- CUSTOMERSPERSONAL TABLE
-- IC Number must be unique
CREATE UNIQUE INDEX idx_customers_icnum 
ON CustomersPersonal(ICNum);

-- Phone Number must be unique
CREATE UNIQUE INDEX idx_customers_phonenum 
ON CustomersPersonal(PhoneNum);

-- Personal Email must be unique
CREATE UNIQUE INDEX idx_customers_personal_email 
ON CustomersPersonal(PersonalEmail);

-- Work Email must be unique
CREATE UNIQUE INDEX idx_customers_work_email 
ON CustomersPersonal(WorkEmail);



-- Indexes for Foreign Keys. These are needed because the reports and forms rely on joins with other tables.
CREATE INDEX idx_exams_customer_id ON Exams(CustomerID);
CREATE INDEX idx_exams_exam_detail_id ON Exams(ExamDetailID);
CREATE INDEX idx_trainings_customer_id ON Trainings(CustomerID);
CREATE INDEX idx_trainings_training_detail_id ON Trainings(TrainingDetailID);


-- Indexes for sorting or filtering. These will help improve the effectiveness of the report generation when filtering by date ranges.
CREATE INDEX idx_exams_examdate ON Exams(ExamDate);
CREATE INDEX idx_trainings_startdate ON Trainings(TrainingStartDate);
CREATE INDEX idx_trainings_enddate ON Trainings(TrainingEndDate);