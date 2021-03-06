"""
This is a metadata scraping plugin for DocumentCloud.

It demonstrates how to write a add-on which can be activated from the
DocumentCloud add-on system and run using Github Actions.  It receives data
from DocumentCloud via the request dispatch and writes data back to
DocumentCloud using the standard API
"""
import sys
from documentcloud.addon import AddOn
import csv


class CustomMetaData(AddOn):
    """An metadata scraping Add-On for DocumentCloud."""

    def main(self):

        if not self.documents:
            self.set_message("Please select at least one document")
            return

        self.set_message("Custom MetaData scraping starting!")

        # getting the input from the frontend, it will be a dictionary of variable length
        # containing the data types the user wants
        # parse through and set the index value in the values array to 1 for every wanted data type
        values = [0] * 12
        for data in self.data:
            if self.data.get(data) == True:
                if data == "ID":
                    values[0] = 1
                elif data == "TITLE":
                    values[1] = 1
                elif data == "PRIVACYLEVEL":
                    values[2] = 1
                elif data == "ASSETURL":
                    values[3] = 1
                elif data == "CONTRIBUTOR":
                    values[4] = 1
                elif data == "CREATEDATDATE":
                    values[5] = 1
                elif data == "DESCRIPTION":
                    values[6] = 1
                elif data == "FULLTEXTURL":
                    values[7] = 1
                elif data == "PDFURL":
                    values[8] = 1
                elif data == "PAGECOUNT":
                    values[9] = 1
                elif data == "TAGS":
                    values[10] = 1
                elif data == "KEYVALUEPAIRS":
                    values[11] = 1

        # preset header + metadata list
        header = [
            "Id",
            "Title",
            "Privacy Level",
            "Asset-Url",
            "Contributor",
            "Created at Date",
            "Description",
            "Full-Text-Url",
            "Pdf-Url",
            "Page Count",
            "Tags",
            "Key Value Pairs",
        ]

        # delete values of 0 from the header because the user does not want them
        Newheader = []
        for head in header:
            # differentiate data types by index
            if values[header.index(head)] == 1:
                Newheader.append(head)

        metadata_list = []  # list of lists containing metadata for each document

        # takes the document object and an empty array as input, and places the document metadata into the array
        def setData(doc, doc_metadata):

            # document description break fix
            try:
                description = doc.description
            except AttributeError:
                description = ""

            doc_metadata = [
                doc.id,
                doc.title,
                doc.access,
                doc.asset_url,
                doc.contributor,
                doc.created_at,
                description,
                doc.full_text_url,
                doc.pdf_url,
                doc.page_count,
            ]

            # separate key values and tags into two separate arrays
            keyvalues = doc.data
            tags = ""

            # are there any tags?
            try:
                tags = keyvalues["_tag"]
                del keyvalues["_tag"]
            except KeyError:
                tags = ""

            doc_metadata.append(tags)
            doc_metadata.append(keyvalues)

            return doc_metadata

        # retrieve information from each document.
        description = "NO DESCRIPTION PRESENT"  # for the edge case with the description not existing
        if self.documents:
            length = len(self.documents)
            for doc_id in self.documents:
                doc = self.client.documents.get(doc_id)

                # set the metadata
                metadata_list.append(setData(doc, []))
        elif self.query:
            i = 0
            documents = self.client.documents.search(self.query)
            for document in documents:
                # set the metadata
                metadata_list.append(setData(document, []))
                i += 1
            length = i

        # go through the accumulated data and delete the data the user does not want from EACH document
        Newdatalist = []
        for document_data in metadata_list:
            wantedData = []
            for data in document_data:
                if values[document_data.index(data)] == 1:
                    wantedData.append(data)
            Newdatalist.append(wantedData)

        # the id of the first document + how many more documents will be the name of the file
        try:
            firstID = metadata_list[0][0]
        except IndexError:
            firstID = ""
            length = 1

        with open(
            "data_for_" + str(firstID) + "+" + str(length - 1) + ".csv", "w+"
        ) as file_:
            writer = csv.writer(file_)

            # FORMAT HEADER
            writer.writerow(Newheader)

            for row in Newdatalist:
                # FORMAT THE DATA
                writer.writerow(row)

            self.upload_file(file_)

        self.set_message("Custom MetaData scraping finished!")


if __name__ == "__main__":
    CustomMetaData().main()
