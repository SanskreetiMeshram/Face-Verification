// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FaceMatchRegistry
 * @dev Tamper-evident registry for face match evidence hashes and reverse image search metadata.
 * No raw biometric data or images are stored on-chain.
 */
contract FaceMatchRegistry {

    struct Record {
        bytes32 evidenceHash;   // SHA-256 hash of canonical evidence JSON
        string resultUrl;       // Actual URL returned by genuine reverse image search
        string platform;        // Detected platform (e.g., Instagram, X, TikTok, YouTube)
        uint256 timestamp;      // Block timestamp of registration
        address submitter;      // Address that submitted the record
    }

    // Incremental counter for registered records
    uint256 public recordCount;

    // Mapping from record ID to Record data
    mapping(uint256 => Record) public records;

    // Mapping from evidenceHash to existence flag & list of record IDs for fast lookup
    mapping(bytes32 => uint256[]) private hashToRecordIds;

    // Event emitted when a new record is registered
    event RecordRegistered(
        uint256 indexed recordId,
        bytes32 indexed evidenceHash,
        string resultUrl,
        string platform,
        uint256 timestamp,
        address indexed submitter
    );

    /**
     * @notice Register a verified face match evidence hash on-chain
     * @param evidenceHash The SHA-256 hash of the canonical evidence JSON
     * @param resultUrl The genuine search result URL
     * @param platform The social media platform classification
     * @return recordId The unique identifier of the registered record
     */
    function registerRecord(
        bytes32 evidenceHash,
        string calldata resultUrl,
        string calldata platform
    ) external returns (uint256) {
        require(evidenceHash != bytes32(0), "Invalid evidence hash");
        require(bytes(resultUrl).length > 0, "Result URL cannot be empty");

        uint256 id = recordCount;
        recordCount++;

        records[id] = Record({
            evidenceHash: evidenceHash,
            resultUrl: resultUrl,
            platform: platform,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        hashToRecordIds[evidenceHash].push(id);

        emit RecordRegistered(
            id,
            evidenceHash,
            resultUrl,
            platform,
            block.timestamp,
            msg.sender
        );

        return id;
    }

    /**
     * @notice Retrieve an existing record by its ID
     * @param id The record ID
     */
    function getRecord(uint256 id)
        external
        view
        returns (
            bytes32 evidenceHash,
            string memory resultUrl,
            string memory platform,
            uint256 timestamp,
            address submitter
        )
    {
        require(id < recordCount, "Record does not exist");
        Record memory record = records[id];

        return (
            record.evidenceHash,
            record.resultUrl,
            record.platform,
            record.timestamp,
            record.submitter
        );
    }

    /**
     * @notice Verify whether a given evidence hash matches the hash recorded at record ID
     * @param id The record ID to check against
     * @param evidenceHash The computed evidence hash to verify
     * @return isMatch True if the hashes match exactly, false otherwise
     */
    function verifyRecord(uint256 id, bytes32 evidenceHash)
        external
        view
        returns (bool isMatch)
    {
        if (id >= recordCount) {
            return false;
        }
        return records[id].evidenceHash == evidenceHash;
    }

    /**
     * @notice Find record IDs associated with a specific evidence hash
     * @param evidenceHash The SHA-256 evidence hash
     */
    function findRecordsByHash(bytes32 evidenceHash)
        external
        view
        returns (uint256[] memory)
    {
        return hashToRecordIds[evidenceHash];
    }
}
