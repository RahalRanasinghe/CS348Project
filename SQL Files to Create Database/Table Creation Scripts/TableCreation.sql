USE synergy_skills;

-- Customers Table
CREATE TABLE CustomersPersonal (
    CustomerID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName VARCHAR(25) NOT NULL,
    LastName VARCHAR(25) NOT NULL,
    Gender CHAR(1) NOT NULL CHECK (Gender IN ('M', 'F', 'N')),
    DOB DATE NOT NULL CHECK (DOB >= '1900-01-01'),
    PhoneNum VARCHAR(10) NOT NULL CHECK (PhoneNum LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    ICNum VARCHAR(10) NOT NULL UNIQUE CHECK (ICNum LIKE '[0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]'),
    Organisation VARCHAR(100) NOT NULL CHECK (Organisation IN (
        'Baiduri Bank',
        'Brunei Fertiliser Industries',
        'Brunei Investment Agency',
        'Brunei Shell Petroleum Sdn Bhd',
        'Dynamik Technologies Sdn Bhd',
        'E-Government National Centre', 
        'International School Brunei',
        'Netcom Computer House',
        'Royal Brunei Airlines',
        'Tech One Global Limited'
    )),
    PersonalEmail VARCHAR(100) NOT NULL CHECK (PersonalEmail LIKE '%@%.%'),
    WorkEmail VARCHAR(100) NOT NULL CHECK (WorkEmail LIKE '%@%.%')
);


-- ExamsDetails Table
CREATE TABLE ExamsDetails (
    ExamDetailID INT IDENTITY(1,1) PRIMARY KEY,
    ExamName VARCHAR(150) NOT NULL,
    ExamProvider VARCHAR(50) NOT NULL CHECK (ExamProvider IN (
        'Microsoft',
        'Cisco',
        'CompTIA',
        'Certiport',
        'PeopleCert',
        'EC-Council',
        'Pearson VUE'
    )),
    NumHours INT CHECK (NumHours > 0) NOT NULL
);

-- Exams Taken Table (Links Customers to Exams)
CREATE TABLE Exams (
    ExamID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL,
    ExamDetailID INT NOT NULL,
    ExamDate DATE CHECK (ExamDate >= '2020-01-01') NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES CustomersPersonal(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (ExamDetailID) REFERENCES ExamsDetails(ExamDetailID) ON DELETE CASCADE
);

-- TrainingsDetails Table
CREATE TABLE TrainingsDetails (
    TrainingDetailID INT IDENTITY(1,1) PRIMARY KEY,
    TrainingName VARCHAR(150) NOT NULL,
    TrainingType VARCHAR(50) NOT NULL CHECK (TrainingType IN ('Virtual', 'In-person', 'On demand')),
    TrainingProvider VARCHAR(50) NOT NULL CHECK (TrainingProvider IN (
        'Microsoft',
        'CompTIA',
        'Cisco',
        'EC-Council',
        'PeopleCert',
        'Certiport',
        'Adobe'
    )),
    NumHours INT NOT NULL CHECK (NumHours > 0)
);

-- Trainings Taken Table (Links Customers to Trainings)
CREATE TABLE Trainings (
    TrainingID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL,
    TrainingDetailID INT NOT NULL,
    TrainingStartDate DATE NOT NULL,
    TrainingEndDate DATE NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES CustomersPersonal(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (TrainingDetailID) REFERENCES TrainingsDetails(TrainingDetailID) ON DELETE CASCADE,
    CONSTRAINT chk_TrainingDates CHECK (TrainingEndDate >= TrainingStartDate) 
);

