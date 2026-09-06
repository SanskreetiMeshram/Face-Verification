// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ContentFingerprintRegistry
 * @dev Tamper-evident registry for cryptographic content fingerprints discovered from genuine reverse-image searches.
 * 
 * IMPORTANT ARCHITECTURAL & PRIVACY PRINCIPLES:
 * 1. ZERO BIOMETRIC EXPOSURE: No raw face images, embeddings, or biometric tensors are ever stored on-chain.
 * 2. CRYPTOGRAPHIC INTEGRITY: Stores only the SHA-256 (bytes32) fingerprint of canonicalized public discovery metadata.
 * 3. TRANSPARENCY: Allows anyone to verify whether a canonical evidence object matches the immutable on-chain record.
 */
contract ContentFingerprintRegistry {

    struct VerificationRecord {
        bytes32 fingerprint;   // SHA-256 hash of canonical discovered metadata JSON
        string sourceUrl;      // Actual discovered public web/social URL
        uint256 timestamp;     // Block timestamp when registered
        address submitter;     // Ethereum address that registered the fingerprint
    }

    // Incremental count of registered records
    uint256 public totalRecords;

    // Mapping from SHA-256 fingerprint (bytes32) to VerificationRecord
    mapping(bytes32 => VerificationRecord) public records;

    // Ordered list of registered fingerprints for index-based retrieval
    bytes32[] public registeredFingerprints;

    // Event emitted when a fingerprint is registered on-chain
    event FingerprintRegistered(
        bytes32 indexed fingerprint,
        string sourceUrl,
        uint256 timestamp,
        address indexed submitter
    );

    /**
     * @notice Register a tamper-evident content fingerprint on-chain.
     * @param fingerprint The bytes32 SHA-256 hash of the canonical discovered metadata.
     * @param sourceUrl The discovered source URL.
     * @return success True if registration succeeded.
     */
    function registerFingerprint(
        bytes32 fingerprint,
        string calldata sourceUrl
    ) external returns (bool) {
        require(fingerprint != bytes32(0), "Invalid fingerprint: cannot be zero");
        require(bytes(sourceUrl).length > 0, "Source URL cannot be empty");
        require(records[fingerprint].timestamp == 0, "Fingerprint already registered on-chain");

        records[fingerprint] = VerificationRecord({
            fingerprint: fingerprint,
            sourceUrl: sourceUrl,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        registeredFingerprints.push(fingerprint);
        totalRecords++;

        emit FingerprintRegistered(
            fingerprint,
            sourceUrl,
            block.timestamp,
            msg.sender
        );

        return true;
    }

    /**
     * @notice Verify whether a given fingerprint exists in the registry.
     * @param fingerprint The bytes32 SHA-256 hash to verify.
     * @return exists True if the record exists on-chain.
     * @return timestamp The block timestamp of registration.
     * @return sourceUrl The registered source URL.
     * @return submitter The address of the submitter.
     */
    function verifyFingerprint(bytes32 fingerprint)
        external
        view
        returns (
            bool exists,
            uint256 timestamp,
            string memory sourceUrl,
            address submitter
        )
    {
        VerificationRecord memory rec = records[fingerprint];
        if (rec.timestamp > 0) {
            return (true, rec.timestamp, rec.sourceUrl, rec.submitter);
        }
        return (false, 0, "", address(0));
    }

    /**
     * @notice Retrieve a record by fingerprint.
     * @param fingerprint The bytes32 SHA-256 hash.
     */
    function getRecord(bytes32 fingerprint)
        external
        view
        returns (
            bytes32 storedFingerprint,
            string memory sourceUrl,
            uint256 timestamp,
            address submitter
        )
    {
        VerificationRecord memory rec = records[fingerprint];
        require(rec.timestamp > 0, "Record does not exist");
        return (rec.fingerprint, rec.sourceUrl, rec.timestamp, rec.submitter);
    }

    /**
     * @notice Retrieve record by numerical index.
     * @param index The 0-indexed position.
     */
    function getRecordByIndex(uint256 index)
        external
        view
        returns (
            bytes32 fingerprint,
            string memory sourceUrl,
            uint256 timestamp,
            address submitter
        )
    {
        require(index < totalRecords, "Index out of bounds");
        bytes32 fp = registeredFingerprints[index];
        VerificationRecord memory rec = records[fp];
        return (rec.fingerprint, rec.sourceUrl, rec.timestamp, rec.submitter);
    }
}
