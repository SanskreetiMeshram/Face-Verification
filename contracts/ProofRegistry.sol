// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProofRegistry
 * @dev Permanent, tamper-evident notarization registry for ProofLink self-identity verifications.
 * Only cryptographic record hashes (bytes32) and canonical non-biometric metadata are stored on-chain.
 * Raw biometric images and embedding vectors are NEVER stored on-chain.
 */
contract ProofRegistry {

    struct Record {
        bytes32 recordHash;     // Combined SHA-256 hash of (selfieHash + profileHash + metadataHash)
        address submitter;      // Address that submitted the notarization
        uint256 timestamp;      // Block timestamp when notarized
        string metadata;        // Canonical JSON string (URL, timestamp, match score, model identifier)
        bool exists;            // Existence flag
    }

    // Mapping from recordHash (bytes32) to Record data
    mapping(bytes32 => Record) private _records;

    // Array of all registered record hashes for enumeration
    bytes32[] private _recordHashes;

    // Event emitted upon successful notarization
    event RecordNotarized(
        bytes32 indexed recordHash,
        address indexed submitter,
        uint256 timestamp
    );

    /**
     * @notice Notarize a verified face match record hash on-chain
     * @param recordHash The 32-byte cryptographic hash of the combined verification evidence
     * @param metadata Canonical JSON metadata string describing the verification
     * @return success Boolean indicating successful registration
     */
    function notarizeRecord(
        bytes32 recordHash,
        string calldata metadata
    ) external returns (bool success) {
        require(recordHash != bytes32(0), "ProofRegistry: invalid record hash");
        require(!_records[recordHash].exists, "ProofRegistry: record already notarized");

        _records[recordHash] = Record({
            recordHash: recordHash,
            submitter: msg.sender,
            timestamp: block.timestamp,
            metadata: metadata,
            exists: true
        });

        _recordHashes.push(recordHash);

        emit RecordNotarized(recordHash, msg.sender, block.timestamp);
        return true;
    }

    /**
     * @notice Verify whether a record hash has been notarized on-chain
     * @param recordHash The 32-byte cryptographic record hash to verify
     * @return exists Whether the record exists in the registry
     * @return submitter The address that submitted the record
     * @return timestamp The block timestamp when the record was registered
     * @return metadata The metadata string stored with the record
     */
    function verify(bytes32 recordHash)
        external
        view
        returns (
            bool exists,
            address submitter,
            uint256 timestamp,
            string memory metadata
        )
    {
        Record memory rec = _records[recordHash];
        return (rec.exists, rec.submitter, rec.timestamp, rec.metadata);
    }

    /**
     * @notice Get the total count of notarized records in the registry
     * @return count Total number of registered records
     */
    function getRecordCount() external view returns (uint256 count) {
        return _recordHashes.length;
    }

    /**
     * @notice Get a registered record by its sequential index
     * @param index The zero-based index of the record
     * @return recordHash The 32-byte record hash
     * @return submitter The submitter address
     * @return timestamp The registration timestamp
     * @return metadata The metadata string
     */
    function getRecordByIndex(uint256 index)
        external
        view
        returns (
            bytes32 recordHash,
            address submitter,
            uint256 timestamp,
            string memory metadata
        )
    {
        require(index < _recordHashes.length, "ProofRegistry: index out of bounds");
        bytes32 rHash = _recordHashes[index];
        Record memory rec = _records[rHash];
        return (rec.recordHash, rec.submitter, rec.timestamp, rec.metadata);
    }
}
