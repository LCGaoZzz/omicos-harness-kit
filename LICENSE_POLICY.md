# License and provenance policy

The kit's original code and templates are Apache-2.0. An adapter generated from a third-party algorithm is a separate work product and must retain the algorithm package's license, copyright notices, citation requirements, and any source-distribution conditions.

The generator records license status as one of:

- `confirmed`: license text or a trusted package metadata field was reviewed;
- `missing`: no license evidence was found;
- `ambiguous`: evidence conflicts or is insufficient;
- `restricted`: the license requires additional permission or has terms that block the intended distribution.

A generated bundle with `missing`, `ambiguous`, or `restricted` license status is not a distributable public package. It may remain a local review artifact.

The generator does not copy algorithm source into the public kit. A manifest may contain a public URL, an optional commit SHA, a license evidence URL, and a digest of generated files. Do not add source archives or user data to this repository.
