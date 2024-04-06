# Recovery Notes

In #40, I proposed two new divisions to capture the differences in the literature: **recoverability testing** and *recovery performance testing*; the following information will be formatted as such to indicate which it is associated with.

## Test Approaches

### Recovery Testing
- *Type of performance-related testing (IEEE, 2022, p. 22)*
- **"Testing … aimed at verifying software restart capabilities after a system crash or other disaster" (Washizaki, 2024, p. 5-9) that ensures it is "restor[ed] … to a state in which it can perform required functions" (IEEE, 2017, p. 370)**
- **May be done through simulations (Washizaki, 2024, p. 5-28)**

### Backup and Recovery Testing
- **Type of reliability testing (IEEE, 2013, p. 2)**
- *"Testing that measures the degree to which system state can be restored from backup within specified parameters of time, cost, completeness, and accuracy in the event of failure" (IEEE, 2013, p. 2)*

### Disaster/Recovery Testing
- **Test type (IEEE, 2022, p. 22)**
- **Also mentioned as "Disaster Recovery" (IEEE, 2013, p. 20), which is "the return to normal operation after a hardware or software failure" (IEEE, 2017, p. 140)**

## Qualities

### Recoverability
- **"How well a system or software can recover data during an interruption or failure" (Washizaki, 2024, p. 7-10; similar in IEEE, 2017, p. 369; OG ISO/IEC, 2011) and "re‐establish the desired state of the system" (IEEE, 2017, p. 369; OG ISO/IEC, 2011)**
- **"Failover testing is … connected with … [its] validation" (Washizaki, 2024, p. 5-9)**
- **Can be tested using *injection slots* (IEEE, 2017, p. 225) and improved through redundancy (IEEE, 2017, p. 370)**
- **A subset of reliability (IEEE, 2017, p. 375) and *usability testing (Washizaki, 2024, p. 5-10)*, and related to survivability (IEEE, 2017, p. 450)**

### Fault Tolerance
- **"A collection of techniques that increase software reliability by detecting errors and then recovering from them or containing their effects if recovery is not possible" (Washizaki, 2024, p. 4-11)**