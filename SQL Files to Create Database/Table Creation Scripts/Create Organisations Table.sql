CREATE TABLE OrganisationList (
    OrganisationID INT PRIMARY KEY IDENTITY(1,1),
    OrganisationName VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO OrganisationList (OrganisationName)
VALUES 
('Baiduri Bank'),
('Brunei Fertiliser Industries'),
('Brunei Investment Agency'),
('Brunei Shell Petroleum Sdn Bhd'),
('Dynamik Technologies Sdn Bhd'),
('E-Government National Centre'),
('International School Brunei'),
('Netcom Computer House'),
('Royal Brunei Airlines'),
('Tech One Global Limited');