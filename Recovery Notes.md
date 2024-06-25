# Recovery Notes

In #40, I proposed two new divisions to capture the differences in the literature: **recoverability testing** and *recovery performance testing*; the following information will be formatted as such to indicate which it is associated with. However, Kam seems to say that "recoverability testing" is a synonym of "recovery testing" (2008, p. 47), so if terminology is used, then it makes more sense to use that term instead.

## Recovery Testing
- *Type of performance-related testing (IEEE, 2022, p. 22)*
- **"Testing … aimed at verifying software restart capabilities after a system crash or other disaster" (Washizaki, 2024, p. 5-9) that ensures it is "restor[ed] … to a state in which it can perform required functions" (IEEE, 2017, p. 370)**
- **May be done through simulations (Washizaki, 2024, p. 5-28)**

## Backup and Recovery Testing
- **Type of reliability testing (IEEE, 2013, p. 2)**
- *"Testing that measures the degree to which system state can be restored from backup within specified parameters of time, cost, completeness, and accuracy in the event of failure" (IEEE, 2013, p. 2)*

## Disaster/Recovery Testing
- **Test type (IEEE, 2022, p. 22)**
- **Also mentioned as "Disaster Recovery" (IEEE, 2013, p. 20), which is "the return to normal operation after a hardware or software failure" (IEEE, 2017, p. 140)**

## Recoverability Testing
- **Given as a synonym of "recovery testing" (Kam, 2008, p. 47)**
- **Connected to failover testing (Washizaki, 2024, p. 5-9) and survivability testing (IEEE, 2017, p. 450)**
- **A sub-approach of reliability testing (IEEE, 2017, p. 375) and *usability testing (Washizaki, 2024, p. 5-10)***
- *Tests "how well a system or software can recover data during an interruption or failure" (Washizaki, 2024, p. 7-10; similar in IEEE, 2017, p. 369; OG ISO/IEC, 2011)* and **"re-establish the desired state of the system" (IEEE, 2017, p. 369; OG ISO/IEC, 2011)**
- **Can be tested using *injection slots* (IEEE, 2017, p. 225) and improved through redundancy (IEEE, 2017, p. 370)**

## Fault Tolerance Testing
- **Explicitly listed as a sub-type[^1] of robustness testing (Firesmith, 2015, p. 56)**
- **Also implied by its quality (ISO/IEC, 2023a; IEEE, 2017, pp. 38, 375; Washizaki, 2024, p. 7-10)**
- **Based on its quality, it's also a sub-type of reliability testing (Washizaki, 2024, p. 4-11), *availability testing (IEEE, 2017, p. 38), and dependability testing (if it exists) (ISO/IEC, 2023a)***
- **Testing the "capability of a product to operate as intended despite the presence of hardware or software faults" (ISO/IEC, 2023a; similar in Washizaki, 2024, p. 7-10) "by detecting errors and then recovering from them or containing their effects if recovery is not possible" (Washizaki, 2024, p. 4-11)"** 

[^1]: Hamburg and Mogyorodi (2024) list it as a synonym of "robustness testing", but this seems incorrect.